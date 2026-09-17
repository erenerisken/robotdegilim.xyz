// @vitest-environment node
import { afterEach, describe, expect, it, vi } from "vitest";
import { Client } from "./Client";
import { convertTime } from "./helpers/convertTime";

function clientWithSchedule(schedule) {
  const client = new Client();
  const responses = {
    "data/scrape_courses/latest.json": { latest: "20261.json" },
    "data/scrape_courses/20261.json": {
      programs: {
        "571": {
          short_name: "CENG",
          courses: {
            "5710213": {
              name: "DATA STRUCTURES",
              sections: {
                "1": {
                  section_number: 1,
                  instructors: [{ name: "STAFF", title: "-" }],
                  criteria: [],
                  schedule,
                },
              },
            },
          },
        },
      },
    },
  };
  vi.spyOn(client.http, "get").mockImplementation(async (url) => {
    const key = url.slice(client.s3BaseUrl.length + 1);
    if (!(key in responses)) throw new Error(`Unexpected URL: ${url}`);
    return { data: responses[key] };
  });
  return client;
}

const slot = (day) => ({
  day,
  start_hour: "08:40",
  end_hour: "10:30",
  classroom: "BMB1",
  building: "BILGISAYAR MUH.",
});

async function lectureTimesOf(client) {
  const [course] = await client.getCourses();
  return course.sections[0].lectureTimes;
}

function clientWithElectives(electives) {
  const client = new Client();
  const responses = {
    "data/scrape_programs/programs.json": {
      programs: {
        "571|1|1|1": {
          short_name: "CENG",
          department_code: "571",
          program_type: "MAJOR",
          education_level: "Bachelor`s",
          electives,
        },
        "120|1|1|1": { short_name: "ARCH", department_code: "120" },
        "240|1|1|1": { short_name: "HIST", department_code: "240" },
      },
    },
    "data/scrape_courses/latest.json": { latest: "20261.json" },
    "data/scrape_courses/20261.json": {
      programs: {
        "120": { short_name: "ARCH", courses: { "1200211": {} } },
        "240": { short_name: "HIST", courses: { "2402205": {} } },
        "642": { short_name: "TURK", courses: { "6420101": {} } },
      },
    },
  };
  vi.spyOn(client.http, "get").mockImplementation(async (url) => {
    const key = url.slice(client.s3BaseUrl.length + 1);
    if (!(key in responses)) throw new Error(`Unexpected URL: ${url}`);
    return { data: responses[key] };
  });
  return client;
}

afterEach(() => vi.restoreAllMocks());

describe("Client.getCourses", () => {
  const weekdays = [
    ["Monday", 1],
    ["Tuesday", 2],
    ["Wednesday", 3],
    ["Thursday", 4],
    ["Friday", 5],
    ["Saturday", 6],
    ["Sunday", 0],
  ];

  it.each(weekdays)("renders a %s lecture on a %s", async (dayName, dayNumber) => {
    const [lectureTime] = await lectureTimesOf(clientWithSchedule([slot(dayName)]));

    expect(lectureTime.day).toBe(dayNumber);
    // The weekly program places a lecture at convertTime(day, ...), so the day
    // numbering has to be the one Date.getDay() returns.
    expect(
      convertTime(lectureTime.day, lectureTime.startHour, lectureTime.startMin)
        .toLocaleDateString("en-US", { weekday: "long" })
    ).toBe(dayName);
  });

  it("parses the rest of the slot alongside the day", async () => {
    const [lectureTime] = await lectureTimesOf(clientWithSchedule([slot("Wednesday")]));

    expect(lectureTime).toEqual({
      classroom: "BMB1",
      day: 3,
      startHour: 8,
      startMin: 40,
      endHour: 10,
      endMin: 30,
    });
  });

  it("drops slots it cannot place instead of defaulting them to a day", async () => {
    const client = clientWithSchedule([
      slot("Someday"),
      { ...slot("Monday"), start_hour: "" },
      slot("Friday"),
    ]);

    expect(await lectureTimesOf(client)).toEqual([expect.objectContaining({ day: 5 })]);
  });
});

describe("Client.getElectives", () => {
  it("reads S3's seven-digit codes and distinguishes open and closed courses", async () => {
    const electives = [
      { code: "1200211", name: "ARCHITECTURAL HISTORY II", category: "NONTECHNICAL ELECTIVE" },
      { code: "5710332", name: "SYSTEMS PROGRAMMING", category: "TECHNICAL ELECTIVE" },
    ];
    const client = clientWithElectives(electives);

    expect(await client.getElectives("CENG")).toEqual([
      { ...electives[0], code: 1200211, stringCode: "ARCH211", isOpen: true },
      { ...electives[1], code: 5710332, stringCode: "CENG332", isOpen: false },
    ]);
  });

  it("preserves department-prefixed codes including four-digit course numbers", async () => {
    const client = clientWithElectives([
      { code: "ARCH 211", name: "ARCHITECTURAL HISTORY II", category: "NONTECHNICAL ELECTIVE" },
      { code: "HIST 2205", name: "HISTORY OF THE TURKISH REVOLUTION I", category: "NONTECHNICAL ELECTIVE" },
      { code: "2402205", name: "HISTORY OF THE TURKISH REVOLUTION I", category: "NONTECHNICAL ELECTIVE" },
      { code: "6420101", name: "TURKISH I", category: "ELECTIVE" },
    ]);

    expect(await client.getElectives("CENG")).toEqual([
      expect.objectContaining({ code: 1200211, stringCode: "ARCH211", isOpen: true }),
      expect.objectContaining({ code: 2402205, stringCode: "HIST2205", isOpen: true }),
      expect.objectContaining({ code: 2402205, stringCode: "HIST2205", isOpen: true }),
      expect.objectContaining({ code: 6420101, stringCode: "TURK101", isOpen: true }),
    ]);
  });

  it("ignores invalid codes without discarding valid numeric IDs", async () => {
    const client = clientWithElectives([
      { code: null },
      { code: "" },
      { code: "1200211invalid" },
      { code: "ARCH 211invalid" },
      { code: "UNKNOWN 211" },
      { code: 1200211, name: "ARCHITECTURAL HISTORY II", category: "NONTECHNICAL ELECTIVE" },
    ]);

    expect(await client.getElectives("CENG")).toEqual([
      expect.objectContaining({ code: 1200211, isOpen: true }),
    ]);
  });
});
