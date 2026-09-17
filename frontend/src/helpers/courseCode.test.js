import { describe, expect, it } from "vitest";
import { courseNumber } from "./courseCode";

describe("courseNumber", () => {
  it.each([
    [5710213, "213"],
    ["5710213", "213"],
    [6420101, "101"],
    // Course numbers run to four digits.
    [2402205, "2205"],
    // Nine of the catalogue's courses sit below 100, e.g. ME 98 and ENGP 11.
    [5690098, "98"],
    [3990011, "11"],
  ])("reads %s as course number %s", (code, expected) => {
    expect(courseNumber(code)).toBe(expected);
  });
});
