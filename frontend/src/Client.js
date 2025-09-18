import axios from "axios";
export class Client {
  constructor() {
    // S3 urls
    this.coursesUrl = "https://s3.amazonaws.com/cdn.robotdegilim.xyz/data.json";
    this.lastUpdatedUrl =
      "https://s3.amazonaws.com/cdn.robotdegilim.xyz/lastUpdated.json";
    this.mustUrl = "https://s3.amazonaws.com/cdn.robotdegilim.xyz/musts.json";
    this.departmentsUrl =
      "https://s3.amazonaws.com/cdn.robotdegilim.xyz/departments.json";
    this.statusUrl =
      "https://s3.amazonaws.com/cdn.robotdegilim.xyz/status.json";
    this.scrapeUrl = "https://robotdegilim-xyz.fly.dev/run-scrape";
  }
  async getLastUpdated() {
    const data = (await axios.get(this.lastUpdatedUrl)).data;
    return data;
  }
  async getMusts(dept, semester) {
    const data = (await axios.get(this.mustUrl)).data;
    return data[dept][semester.toString()];
  }
  async getCourses() {
    const data = (await axios.get(this.coursesUrl)).data;
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

  async sendUpdateRequest() {
    try {
      // Fetch the status from S3
      const statusResponse = await axios.get(this.statusUrl);
      const statusData = statusResponse.data;

      // Check if the status is 'idle'
      if (statusData.status === "idle") {
        // Send request to the backend to start the scraping
        const updateResponse = await axios.get(this.scrapeUrl);
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
