import axios from "axios";

const DEFAULT_S3_BASE_URL = "https://s3.amazonaws.com/cdn.robotdegilim.xyz";
const DEFAULT_BACKEND_BASE_URL = "https://robotdegilim-xyz.fly.dev";

const S3_FILE_KEYS = Object.freeze({
  courses: "data.json",
  lastUpdated: "lastUpdated.json",
  musts: "musts.json",
  departments: "departments.json",
  status: "status.json",
  nteAvailable: "nteAvailable.json",
});

function _normalizeBaseUrl(url, fallback) {
  const raw = (url || fallback || "").trim();
  return raw.replace(/\/+$/, "");
}

function _joinUrl(base, key) {
  return `${base}/${key}`;
}

export class Client {
  constructor() {
    const s3BaseUrl = _normalizeBaseUrl(
      process.env.REACT_APP_S3_BASE_URL,
      DEFAULT_S3_BASE_URL
    );
    const backendBaseUrl = _normalizeBaseUrl(
      process.env.REACT_APP_BACKEND_BASE_URL,
      DEFAULT_BACKEND_BASE_URL
    );

    this.coursesUrl = _joinUrl(s3BaseUrl, S3_FILE_KEYS.courses);
    this.lastUpdatedUrl = _joinUrl(s3BaseUrl, S3_FILE_KEYS.lastUpdated);
    this.mustUrl = _joinUrl(s3BaseUrl, S3_FILE_KEYS.musts);
    this.departmentsUrl = _joinUrl(s3BaseUrl, S3_FILE_KEYS.departments);
    this.statusUrl = _joinUrl(s3BaseUrl, S3_FILE_KEYS.status);
    this.scrapeUrl = _joinUrl(backendBaseUrl, "run-scrape");
    this.nteUrl = _joinUrl(s3BaseUrl, S3_FILE_KEYS.nteAvailable);

    this.http = axios.create({
      timeout: Number(process.env.REACT_APP_API_TIMEOUT_MS || 15000),
    });
  }
  async getLastUpdated() {
    const data = (await this.http.get(this.lastUpdatedUrl)).data;
    return data;
  }
  async getMusts(dept, semester) {
    const data = (await this.http.get(this.mustUrl)).data;
    return data[dept][semester.toString()];
  }
  async getCourses() {
    const data = (await this.http.get(this.coursesUrl)).data;
    const courses = Array(0);
    // eslint-disable-next-line
    Object.keys(data).map((code) => {
      const courseToPush = {
        code: code,
        abbreviation: data[code]["Course Name"].slice(
          0,
          data[code]["Course Name"].search(" ")
        ),
        name: data[code]["Course Name"].slice(
          data[code]["Course Name"].search("-") + 2
        ),
        category: 0,
        sections: Array(0),
      };
      const sectionNumbers = Object.keys(data[code]["Sections"]);
      // eslint-disable-next-line
      sectionNumbers.map((sn) => {
        const s = data[code]["Sections"][sn];
        const sectionToPush = {
          instructor: s["i"][0],
          sectionNumber: sn,
          criteria: Array(0),
          minYear: 0,
          maxYear: 0,
          lectureTimes: Array(0),
        };
        // eslint-disable-next-line
        s["t"].map((t) => {
          sectionToPush.lectureTimes.push({
            classroom: t["p"],
            day: t["d"],
            startHour: parseInt(t["s"].slice(0, t["s"].search(":"))),
            startMin: parseInt(t["s"].slice(t["s"].search(":") + 1)),
            endHour: parseInt(t["e"].slice(0, t["e"].search(":"))),
            endMin: parseInt(t["e"].slice(t["e"].search(":") + 1)),
          });
        });
        // eslint-disable-next-line
        s["c"].map((c) => {
          sectionToPush.criteria.push({
            dept: c["d"],
            surnameStart: c["s"],
            surnameEnd: c["e"],
          });
        });
        courseToPush.sections.push(sectionToPush);
      });
      courses.push(courseToPush);
    });
    return courses;
  }
  async getNTEs() {
    const data = (await this.http.get(this.nteUrl)).data;
    return data;
  }

  async sendUpdateRequest() {
    try {
      // Fetch the status from S3
      const statusResponse = await this.http.get(this.statusUrl);
      const statusData = statusResponse.data;
      const status = String(statusData?.status || "").toLowerCase();

      // Check if the status is 'idle'
      if (status === "idle") {
        // Send request to the backend to start the scraping
        const updateResponse = await this.http.get(this.scrapeUrl);
        const updateData = updateResponse.data; // No need for .json() with axios
        console.log("Response of Update request:", updateData);
        // Handle response data or update component state if needed
      } else {
        console.log("Status is not idle. No update request sent.");
      }
    } catch (error) {
      console.error("Failed to send update request:", error);
      // Handle errors
    }
  }
}
