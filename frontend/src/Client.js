import axios from "axios";
import { courseNumber } from "./helpers/courseCode";

const DEFAULT_S3_BASE_URL = "https://s3.amazonaws.com/cdn.robotdegilim.xyz";
const DEFAULT_BACKEND_BASE_URL = "https://robotdegilim-xyz-backend.fly.dev";
// METU's academic catalogue keys a programme by the same three digits its
// course codes start with, e.g. CENG -> 571.
const CATALOG_PROGRAM_URL = "https://catalog.metu.edu.tr/program.php";

function _normalizeBaseUrl(url, fallback) {
  const raw = (url || fallback || "").trim();
  return raw.replace(/\/+$/, "");
}

function _joinUrl(base, key) {
  return `${base}/${key}`;
}

// Whether a department's students may register for a section. Nearly half the
// catalogue's sections carry no criteria at all, which leaves them open to
// everyone; the rest have to name the department or be given to "ALL". Surname
// and CGPA decide which section a student lands in, not whether the course is
// theirs to take, so neither narrows this.
function sectionAdmits(section, dept) {
  const criteria = section.criteria || [];

  return (
    criteria.length === 0 ||
    criteria.some((c) => c.given_dept === "ALL" || c.given_dept === dept)
  );
}

export class Client {
  constructor() {
    const env = import.meta.env;
    this.s3BaseUrl = _normalizeBaseUrl(env.VITE_S3_BASE_URL || env.REACT_APP_S3_BASE_URL, DEFAULT_S3_BASE_URL);
    const backendBaseUrl = _normalizeBaseUrl(env.VITE_BACKEND_BASE_URL || env.REACT_APP_BACKEND_BASE_URL, DEFAULT_BACKEND_BASE_URL);

    this.scrapeUrl = _joinUrl(backendBaseUrl, "api/v1/jobs/scrape_courses"); 

    this.http = axios.create({
      // The course catalogue is several megabytes, which takes well over 15s on
      // a phone connection.
      timeout: Number(env.VITE_API_TIMEOUT_MS || env.REACT_APP_API_TIMEOUT_MS || 30000),
    });

    this._pending = {};
  }

  // Remembers the request rather than its result, so a caller that asks while
  // one is still in flight joins it instead of starting a second download of
  // the same multi-megabyte file. A failed request is forgotten, leaving a
  // retry free to start a fresh one.
  _once(key, run) {
    if (!this._pending[key]) {
      this._pending[key] = run().catch((error) => {
        this._pending[key] = null;
        throw error;
      });
    }
    return this._pending[key];
  }

  _getLatestCourseData() {
    return this._once("courses", async () => {
      // Discover latest
      const latestPointerUrl = _joinUrl(this.s3BaseUrl, "data/scrape_courses/latest.json");
      const pointerResponse = await this.http.get(latestPointerUrl);
      const latestFilename = pointerResponse.data.latest; // e.g. "20261.json"

      const coursesUrl = _joinUrl(this.s3BaseUrl, `data/scrape_courses/${latestFilename}`);
      const coursesResponse = await this.http.get(coursesUrl);

      return coursesResponse.data;
    });
  }

  _getProgramsData() {
    return this._once("programs", async () => {
      const programsUrl = _joinUrl(this.s3BaseUrl, "data/scrape_programs/programs.json");
      const programsResponse = await this.http.get(programsUrl);

      return programsResponse.data;
    });
  }

  // Maps a department's abbreviation to the three digits its course codes start
  // with, e.g. "ENG" -> "639". programs.json only lists the departments that
  // award a degree; 48 more teach courses without awarding one, ENG, TURK and
  // HST among them, and curricula are full of those. Take them from the course
  // catalogue, which covers every department.
  _getDepartmentCodes() {
    return this._once("departmentCodes", async () => {
      const [programsData, coursesData] = await Promise.all([
        this._getProgramsData(),
        this._getLatestCourseData(),
      ]);

      const departmentCodes = new Map();
      Object.values(programsData.programs).forEach((program) => {
        if (program.short_name && !departmentCodes.has(program.short_name)) {
          departmentCodes.set(program.short_name, String(program.department_code));
        }
      });
      Object.entries(coursesData.programs).forEach(([departmentCode, department]) => {
        if (department.short_name && !departmentCodes.has(department.short_name)) {
          departmentCodes.set(department.short_name, departmentCode);
        }
      });

      return departmentCodes;
    });
  }

  async getLastUpdated() {
    const data = await this._getLatestCourseData();
    return {
      u: new Date(data.metadata.updated_at).toLocaleString(),
      t: "Semester:" + data.metadata.semester_name
    };
  }

  async getCourses() {
    const data = await this._getLatestCourseData();
    const courses = [];
    
    // Date.getDay() numbering: the weekly program renders a lecture on
    // 2021-02-14 + day, and 2021-02-14 is a Sunday.
    const dayMap = {
      Sunday: 0,
      Monday: 1,
      Tuesday: 2,
      Wednesday: 3,
      Thursday: 4,
      Friday: 5,
      Saturday: 6
    };

    // programs dict is { "642": { "short_name": "TURK", "name": "Turkish Language", "courses": { "6420101": { ... } } } }
    for (const [deptCode, deptData] of Object.entries(data.programs)) {
      const deptShortName = deptData.short_name;
      
      for (const [courseCode, courseData] of Object.entries(deptData.courses)) {
        const courseToPush = {
          code: parseInt(courseCode, 10), // e.g. 6420101
          abbreviation: `${deptShortName} ${courseNumber(courseCode)}`, // e.g. TURK 101
          name: courseData.name,
          category: 0, // Fallback, could map from courseData.type
          sections: [],
        };
        
        for (const [sectionNumStr, sectionData] of Object.entries(courseData.sections)) {
          const sectionToPush = {
            instructor: sectionData.instructors.length > 0 ? sectionData.instructors[0].name : "STAFF",
            sectionNumber: sectionData.section_number,
            criteria: [],
            minYear: 0,
            maxYear: 0,
            lectureTimes: [],
          };
          
          if (sectionData.schedule) {
            sectionData.schedule.forEach((t) => {
              const day = dayMap[t.day];
              if (day !== undefined && t.start_hour && t.end_hour) {
                 sectionToPush.lectureTimes.push({
                   classroom: t.classroom || t.building || "TBA",
                   day,
                   startHour: parseInt(t.start_hour.split(":")[0], 10),
                   startMin: parseInt(t.start_hour.split(":")[1], 10),
                   endHour: parseInt(t.end_hour.split(":")[0], 10),
                   endMin: parseInt(t.end_hour.split(":")[1], 10),
                 });
              }
            });
          }
          
          if (sectionData.criteria && sectionData.criteria.length > 0) {
             // Take minYear and maxYear from first criteria if available
             sectionToPush.minYear = sectionData.criteria[0].year.min || 0;
             sectionToPush.maxYear = sectionData.criteria[0].year.max || 0;
             
             sectionData.criteria.forEach((c) => {
               sectionToPush.criteria.push({
                 dept: c.given_dept || "ALL",
                 surnameStart: c.start_char || "AA",
                 surnameEnd: c.end_char || "ZZ",
               });
             });
          } else {
             sectionToPush.criteria.push({
                 dept: "ALL",
                 surnameStart: "AA",
                 surnameEnd: "ZZ",
             });
          }
          
          courseToPush.sections.push(sectionToPush);
        }
        
        courses.push(courseToPush);
      }
    }
    
    return courses;
  }

  // Every department teaching this semester, taken from the catalogue the app
  // has already downloaded. programs.json names a handful more, but it weighs
  // eight megabytes and this is only a lookup table.
  async getDepartments() {
    const data = await this._getLatestCourseData();

    return Object.values(data.programs)
      .filter((department) => department.short_name)
      .map((department) => ({
        abbreviation: department.short_name,
        name: department.name || "",
      }))
      .sort((a, b) => a.abbreviation.localeCompare(b.abbreviation, "tr"));
  }

  // programs.json lists a department once per education level and once more
  // for each double major and minor variant. The undergraduate major is the
  // one the student filling in this form is following.
  _findBachelorProgram(programsData, dept) {
    return Object.values(programsData.programs).find(
      (p) =>
        p.short_name === dept &&
        p.program_type === "MAJOR" &&
        p.education_level === "Bachelor`s"
    );
  }

  // The catalogue only publishes an undergraduate curriculum for the bachelor's
  // majors, which is the same set getMusts can answer for. Anything else, a
  // graduate-only abbreviation or a department that teaches without awarding a
  // degree, has no page to link to.
  async getCurriculumUrl(dept) {
    const programsData = await this._getProgramsData();
    const program = this._findBachelorProgram(programsData, dept);

    if (!program || !program.program_code) return null;

    const facultyProgram = encodeURIComponent(program.program_code);
    return `${CATALOG_PROGRAM_URL}?fac_prog=${facultyProgram}&submenuheader=2`;
  }

  async getMusts(dept, semester) {
    const programsData = await this._getProgramsData();
    const departmentCodes = await this._getDepartmentCodes();

    const targetProgram = this._findBachelorProgram(programsData, dept);
    
    if (!targetProgram || !targetProgram.curriculum[semester]) {
      throw new Error("Must courses not found for this department and semester");
    }
    
    const semCurriculum = targetProgram.curriculum[semester];
    
    // Filter out electives and build 7 digit codes
    const mustCodes = semCurriculum.courses
      .filter(c => !c.is_elective)
      .map(c => {
        // e.g. "HIST 2205" -> ["HIST", "2205"]
        // e.g. "ARCH 103" -> ["ARCH", "103"]
        const parts = c.code.split(" ");
        if (parts.length < 2) return null; // Unparseable
        
        const abbr = parts[0];
        const numPart = parts[1];

        const programCode = departmentCodes.get(abbr); // e.g. "120"
        if (!programCode) return null;

        // Pad the numeric part to 4 digits always. 103 -> 0103. 2205 -> 2205.
        const paddedNum = numPart.padStart(4, "0");
        
        const sevenDigit = parseInt(programCode + paddedNum, 10);
        return sevenDigit;
      }).filter(c => c !== null);
      
    return mustCodes;
  }

  // The electives a department can actually sign up for: the ones its
  // curriculum lists, that the catalogue offers this semester, and that keep at
  // least one section its students are let into. sectionNumbers names those
  // sections, so the ones held for other departments are never offered either.
  async getElectives(dept) {
    const programsData = await this._getProgramsData();
    const departmentCodes = await this._getDepartmentCodes();
    const targetProgram = this._findBachelorProgram(programsData, dept);
    
    if (!targetProgram || !targetProgram.electives) {
      return [];
    }
    
    // We need to cross reference with open courses
    const openCoursesData = await this._getLatestCourseData();
    const departmentAbbreviations = new Map();
    Object.values(programsData.programs).forEach(program => {
      const departmentCode = String(program.department_code);
      if (program.short_name && !departmentAbbreviations.has(departmentCode)) {
        departmentAbbreviations.set(departmentCode, program.short_name);
      }
    });
    const openCourses = new Map();
    Object.entries(openCoursesData.programs).forEach(([departmentCode, prog]) => {
       // The course catalog also includes departments without a degree program (e.g. TURK).
       if (prog.short_name) departmentAbbreviations.set(departmentCode, prog.short_name);
       Object.entries(prog.courses).forEach(([cCode, course]) => {
          openCourses.set(parseInt(cCode, 10), course);
       });
    });

    // A curriculum lists the same course twice often enough that it is worth
    // saying so: 740 of them across the catalogue repeat a code under one
    // heading. Repeats under two headings are not duplicates, because the two
    // headings are filtered separately.
    const listed = new Set();
    
    const electivesProcessed = targetProgram.electives.map(e => {
        const rawCode = String(e.code ?? "").trim();
        const parts = rawCode.split(/\s+/);
        let sevenDigitCode = null;
        // S3 electives already use seven-digit IDs; retain support for codes like "HIST 2205".
        if (/^\d{7}$/.test(rawCode)) {
          sevenDigitCode = Number(rawCode);
        } else if (parts.length === 2 && /^\d{1,4}$/.test(parts[1])) {
          const abbr = parts[0];
          const numPart = parts[1];
          const programCode = departmentCodes.get(abbr);
          if (programCode) {
            const paddedNum = numPart.padStart(4, "0");
            sevenDigitCode = parseInt(programCode + paddedNum, 10);
          }
        }

        const openCourse = sevenDigitCode === null ? undefined : openCourses.get(sevenDigitCode);
        if (!openCourse) return null;

        const sectionNumbers = Object.values(openCourse.sections || {})
          .filter((section) => sectionAdmits(section, dept))
          .map((section) => section.section_number);
        if (sectionNumbers.length === 0) return null;

        const listing = `${sevenDigitCode}|${e.category}`;
        if (listed.has(listing)) return null;
        listed.add(listing);

        const numericCode = String(sevenDigitCode);
        const abbreviation = departmentAbbreviations.get(numericCode.slice(0, 3));
        const stringCode = abbreviation
          ? `${abbreviation} ${courseNumber(numericCode)}`
          : rawCode;

        return {
           code: sevenDigitCode,
           stringCode,
           name: e.name,
           category: e.category,
           sectionNumbers,
        };
    }).filter(e => e !== null);
    
    return electivesProcessed;
  }

  async sendUpdateRequest() {
    try {
      const lockUrl = _joinUrl(this.s3BaseUrl, "locks/worker.lock");
      let isLocked = false;

      try {
        await this.http.get(`${lockUrl}?t=${new Date().getTime()}`);
        isLocked = true;
      } catch (e) {
        // S3 returns 404 (or 403 if listing is denied) when a file doesn't exist
        if (e.response && (e.response.status === 404 || e.response.status === 403)) {
          isLocked = false;
        } else {
          console.warn("Could not check worker lock status:", e.message);
          isLocked = true; // Assume locked to be safe and save Fly.io traffic
        }
      }

      if (!isLocked) {
        console.log("Worker is idle. Pinging backend to check for stale data...");
        const updateResponse = await this.http.post(this.scrapeUrl);
        console.log("Response of update request:", updateResponse.data);
      } else {
        console.log("Worker is currently busy (lock file exists). Skipping ping to Fly.io to save traffic.");
      }
    } catch (error) {
      console.error("Failed to send update request:", error);
    }
  }
}

// One instance for the whole app: every screen needs the same catalogue, and a
// per-call client would download those megabytes again each time.
export const client = new Client();
