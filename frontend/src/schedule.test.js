import { describe, expect, it } from "vitest";
import { compute_schedule } from "./schedule";

const section = (sectionNumber, day, startHour, endHour) => ({
  sectionNumber,
  toggle: true,
  criteria: [{ dept: "ALL", surnameStart: "AA", surnameEnd: "ZZ" }],
  lectureTimes: [{ day, startHour, startMin: 0, endHour, endMin: 0 }],
});

describe("compute_schedule", () => {
  it("returns every non-conflicting section combination", () => {
    const courses = [
      { code: "A", checkSurname: false, checkDepartment: false, checkCollision: true, sections: [section(1, 0, 8, 9)] },
      { code: "B", checkSurname: false, checkDepartment: false, checkCollision: true, sections: [section(1, 1, 8, 9)] },
    ];
    expect(compute_schedule("AA", "CENG", 1, courses, [])).toHaveLength(1);
  });
});

// Controls only ever forwards the first two letters of the surname.
const admits = (surname, surnameStart, surnameEnd) =>
  compute_schedule(
    surname.slice(0, 2),
    "EE",
    0,
    [
      {
        code: "A",
        checkSurname: true,
        checkDepartment: false,
        checkCollision: true,
        sections: [
          {
            sectionNumber: 1,
            toggle: true,
            criteria: [{ dept: "ALL", surnameStart, surnameEnd }],
            lectureTimes: [{ day: 1, startHour: 8, startMin: 40, endHour: 10, endMin: 30 }],
          },
        ],
      },
    ],
    []
  ).length > 0;

describe("surname criteria", () => {
  // A range whose ends share a first letter used to admit nobody at all, which
  // is how MATH 119's AA-AZ section for EE went missing for surnames like
  // ARSLAN.
  it.each([
    ["ARSLAN", "AA", "AZ"],
    ["AKIN", "AA", "AZ"],
    ["ARI", "AA", "AY"],
    ["KARA", "KA", "KZ"],
    ["YILMAZ", "YA", "YZ"],
  ])("admits %s to a %s-%s section", (surname, start, end) =>
    expect(admits(surname, start, end)).toBe(true)
  );

  it.each([
    ["GUNDUZ", "AA", "ZZ"],
    ["CAN", "AA", "FF"],
    ["ÖZKAN", "OA", "ÖZ"],
  ])("still admits %s to a %s-%s section", (surname, start, end) =>
    expect(admits(surname, start, end)).toBe(true)
  );

  it.each([
    ["ARSLAN", "BA", "BZ"],
    ["YILMAZ", "AA", "FF"],
    ["AKIN", "AL", "AZ"],
    ["AZAK", "AA", "AY"],
  ])("keeps %s out of a %s-%s section", (surname, start, end) =>
    expect(admits(surname, start, end)).toBe(false)
  );

  it("admits both ends of the range", () => {
    expect(admits("AA", "AA", "AZ")).toBe(true);
    expect(admits("AZ", "AA", "AZ")).toBe(true);
  });
});
