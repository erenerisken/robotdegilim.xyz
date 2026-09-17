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

function clientWithCurriculum(courses) {
  const client = new Client();
  const responses = {
    "data/scrape_programs/programs.json": {
      programs: {
        "571|1|1|1": {
          short_name: "CENG",
          program_code: "571",
          department_code: "571",
          program_type: "MAJOR",
          education_level: "Bachelor`s",
          curriculum: { 3: { semester_number: 3, courses } },
        },
        "57120|2|1|1": {
          short_name: "CENG",
          program_code: "57120",
          department_code: "571",
          program_type: "DOUBLE MAJOR",
          education_level: "Bachelor`s",
        },
        "555|1|62|2": {
          short_name: "MI",
          program_code: "555",
          department_code: "555",
          program_type: "MAJOR",
          education_level: "Master's (with thesis)",
        },
        "236|1|1|1": { short_name: "MATH", department_code: "236" },
      },
    },
    "data/scrape_courses/latest.json": { latest: "20261.json" },
    // ENG and TURK teach courses without awarding a degree, so they appear here
    // and nowhere in programs.json.
    "data/scrape_courses/20261.json": {
      programs: {
        "571": { short_name: "CENG", courses: {} },
        "236": { short_name: "MATH", courses: {} },
        "639": { short_name: "ENG", courses: {} },
        "642": { short_name: "TURK", courses: {} },
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

const must = (code) => ({ code, is_elective: false });

function countingClient(onGet) {
  const client = new Client();
  const calls = [];
  vi.spyOn(client.http, "get").mockImplementation(async (url) => {
    const key = url.slice(client.s3BaseUrl.length + 1);
    calls.push(key);
    return onGet(key);
  });
  return { client, calls };
}

const CATALOGUE = {
  "data/scrape_courses/latest.json": { latest: "20261.json" },
  "data/scrape_courses/20261.json": {
    metadata: { semester_name: "2026-2027 Fall", updated_at: "2026-09-06T16:45:12+03:00" },
    programs: { "571": { short_name: "CENG", courses: {} } },
  },
  "data/scrape_programs/programs.json": { programs: {} },
};

afterEach(() => vi.restoreAllMocks());

describe("Client request sharing", () => {
  it("downloads the catalogue once however many callers ask", async () => {
    const { client, calls } = countingClient(async (key) => ({ data: CATALOGUE[key] }));

    await Promise.all([client.getCourses(), client.getLastUpdated()]);
    await client.getCourses();

    expect(calls.filter((k) => k.endsWith("20261.json"))).toHaveLength(1);
    expect(calls.filter((k) => k.endsWith("latest.json"))).toHaveLength(1);
  });

  it("shares one request between callers that ask while it is in flight", async () => {
    let release;
    const gate = new Promise((resolve) => {
      release = resolve;
    });
    const { client, calls } = countingClient(async (key) => {
      await gate;
      return { data: CATALOGUE[key] };
    });

    const both = Promise.all([client.getCourses(), client.getCourses()]);
    release();
    await both;

    expect(calls.filter((k) => k.endsWith("20261.json"))).toHaveLength(1);
  });

  it("lets a retry start over after a failure", async () => {
    let failing = true;
    const { client, calls } = countingClient(async (key) => {
      if (failing) throw new Error("offline");
      return { data: CATALOGUE[key] };
    });

    await expect(client.getCourses()).rejects.toThrow("offline");
    failing = false;
    await expect(client.getCourses()).resolves.toEqual([]);

    expect(calls.filter((k) => k.endsWith("latest.json"))).toHaveLength(2);
  });
});

describe("Client.getCurriculumUrl", () => {
  it("points at the catalog page for the department's undergraduate major", async () => {
    const client = clientWithCurriculum([must("CENG 223")]);

    expect(await client.getCurriculumUrl("CENG")).toBe(
      "https://catalog.metu.edu.tr/program.php?fac_prog=571&submenuheader=2"
    );
  });

  it("has no page for a department that awards no bachelor's degree", async () => {
    const client = clientWithCurriculum([must("CENG 223")]);

    // MI is a graduate-only programme, TURK teaches without awarding a degree
    // and ZZZ is a typo.
    expect(await client.getCurriculumUrl("MI")).toBeNull();
    expect(await client.getCurriculumUrl("TURK")).toBeNull();
    expect(await client.getCurriculumUrl("ZZZ")).toBeNull();
  });
});

describe("Client.getMusts", () => {
  it("keeps courses taught by departments that award no degree", async () => {
    const client = clientWithCurriculum([
      must("CENG 223"),
      must("ENG 211"),
      must("TURK 105"),
    ]);

    expect(await client.getMusts("CENG", 3)).toEqual([5710223, 6390211, 6420105]);
  });

  it("pads three-digit numbers and leaves four-digit ones alone", async () => {
    const client = clientWithCurriculum([must("MATH 219"), must("CENG 2205")]);

    expect(await client.getMusts("CENG", 3)).toEqual([2360219, 5712205]);
  });

  it("skips electives and codes it cannot resolve", async () => {
    const client = clientWithCurriculum([
      { code: "CENG 300", is_elective: true },
      must("SCE 322"),
      must("CENG213"),
      must("CENG 223"),
    ]);

    expect(await client.getMusts("CENG", 3)).toEqual([5710223]);
  });

  it("reports a department or semester it has no curriculum for", async () => {
    await expect(clientWithCurriculum([must("CENG 223")]).getMusts("CENG", 4))
      .rejects.toThrow(/not found/i);
  });
});

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

  it("labels a course with its department and course number", async () => {
    const [course] = await clientWithSchedule([slot("Monday")]).getCourses();

    expect(course.abbreviation).toBe("CENG 213");
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
      { ...electives[0], code: 1200211, stringCode: "ARCH 211", isOpen: true },
      { ...electives[1], code: 5710332, stringCode: "CENG 332", isOpen: false },
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
      expect.objectContaining({ code: 1200211, stringCode: "ARCH 211", isOpen: true }),
      expect.objectContaining({ code: 2402205, stringCode: "HIST 2205", isOpen: true }),
      expect.objectContaining({ code: 2402205, stringCode: "HIST 2205", isOpen: true }),
      expect.objectContaining({ code: 6420101, stringCode: "TURK 101", isOpen: true }),
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
