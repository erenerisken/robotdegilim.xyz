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
