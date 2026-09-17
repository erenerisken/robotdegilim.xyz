import axios from "axios";

const DEFAULT_S3_BASE_URL = "https://s3.amazonaws.com/cdn.robotdegilim.xyz";
const DEFAULT_BACKEND_BASE_URL = "https://robotdegilim-xyz.fly.dev";

function _normalizeBaseUrl(url, fallback) {
  const raw = (url || fallback || "").trim();
  return raw.replace(/\/+$/, "");
}

function _joinUrl(base, key) {
  return `${base}/${key}`;
}

export class Client {
  constructor() {
    const env = import.meta.env;
    this.s3BaseUrl = _normalizeBaseUrl(env.VITE_S3_BASE_URL || env.REACT_APP_S3_BASE_URL, DEFAULT_S3_BASE_URL);
    const backendBaseUrl = _normalizeBaseUrl(env.VITE_BACKEND_BASE_URL || env.REACT_APP_BACKEND_BASE_URL, DEFAULT_BACKEND_BASE_URL);

    this.scrapeUrl = _joinUrl(backendBaseUrl, "api/v1/jobs/scrape_courses"); 

    this.http = axios.create({
      timeout: Number(env.VITE_API_TIMEOUT_MS || env.REACT_APP_API_TIMEOUT_MS || 15000),
    });

    this._coursesDataCache = null;
    this._programsDataCache = null;
  }

  async _getLatestCourseData() {
    if (this._coursesDataCache) return this._coursesDataCache;

    // Discover latest
    const latestPointerUrl = _joinUrl(this.s3BaseUrl, "data/scrape_courses/latest.json");
    const pointerResponse = await this.http.get(latestPointerUrl);
    const latestFilename = pointerResponse.data.latest; // e.g. "20261.json"

    const coursesUrl = _joinUrl(this.s3BaseUrl, `data/scrape_courses/${latestFilename}`);
    const coursesResponse = await this.http.get(coursesUrl);
    
    this._coursesDataCache = coursesResponse.data;
    return this._coursesDataCache;
  }

  async _getProgramsData() {
    if (this._programsDataCache) return this._programsDataCache;

    const programsUrl = _joinUrl(this.s3BaseUrl, "data/scrape_programs/programs.json");
    const programsResponse = await this.http.get(programsUrl);
    
    this._programsDataCache = programsResponse.data;
    return this._programsDataCache;
  }

  async getLastUpdated() {
    const data = await this._getLatestCourseData();
    return data.metadata.updated_at;
  }

  async getCourses() {
    const data = await this._getLatestCourseData();
    const courses = [];
    
    const dayMap = {
      Monday: 0,
      Tuesday: 1,
      Wednesday: 2,
      Thursday: 3,
      Friday: 4,
      Saturday: 5,
      Sunday: 6
    };

    // programs dict is { "642": { "short_name": "TURK", "name": "Turkish Language", "courses": { "6420101": { ... } } } }
    for (const [deptCode, deptData] of Object.entries(data.programs)) {
      const deptShortName = deptData.short_name;
      
      for (const [courseCode, courseData] of Object.entries(deptData.courses)) {
        const courseToPush = {
          code: parseInt(courseCode, 10), // e.g. 6420101
          abbreviation: deptShortName,
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
              if (t.day && t.start_hour && t.end_hour) {
                 sectionToPush.lectureTimes.push({
                   classroom: t.classroom || t.building || "TBA",
                   day: dayMap[t.day] !== undefined ? dayMap[t.day] : 0,
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

  async getMusts(dept, semester) {
    const programsData = await this._getProgramsData();
    
    // Find program by short_name (e.g. "ARCH") and program_type === "MAJOR"
    const targetProgram = Object.values(programsData.programs).find(p => p.short_name === dept && p.program_type === "MAJOR" && p.education_level === "Bachelor`s");
    
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
        
        // Find dept base code from programsData
        const deptProg = Object.values(programsData.programs).find(p => p.short_name === abbr);
        if (!deptProg) return null;
        
        const programCode = deptProg.department_code; // e.g. "120"
        
        // Pad the numeric part to 4 digits always. 103 -> 0103. 2205 -> 2205.
        const paddedNum = numPart.padStart(4, "0");
        
        const sevenDigit = parseInt(programCode + paddedNum, 10);
        return sevenDigit;
      }).filter(c => c !== null);
      
    return mustCodes;
  }

  // Replaces getNTEs -> getElectives
  async getElectives(dept) {
    const programsData = await this._getProgramsData();
    const targetProgram = Object.values(programsData.programs).find(p => p.short_name === dept && p.program_type === "MAJOR" && p.education_level === "Bachelor`s");
    
    if (!targetProgram || !targetProgram.electives) {
      return [];
    }
    
    // We need to cross reference with open courses
    const openCoursesData = await this._getLatestCourseData();
    // Build a set of open course codes
    const openCourseCodes = new Set();
    Object.values(openCoursesData.programs).forEach(prog => {
       Object.keys(prog.courses).forEach(cCode => {
          openCourseCodes.add(parseInt(cCode, 10));
       });
    });
    
    const electivesProcessed = targetProgram.electives.map(e => {
        return {
           code: parseInt(e.code, 10),
           name: e.name,
           category: e.category,
           isOpen: openCourseCodes.has(parseInt(e.code, 10))
        };
    });
    
    return electivesProcessed;
  }

  async sendUpdateRequest() {
    try {
      // With the new queue worker, we just fire off the scrape courses endpoint
      // We no longer strictly need to check 'status.json' for 'idle' as the worker deduplicates
      const updateResponse = await this.http.post(this.scrapeUrl, {});
      console.log("Response of Update request:", updateResponse.data);
    } catch (error) {
      console.error("Failed to send update request:", error);
    }
  }
}
