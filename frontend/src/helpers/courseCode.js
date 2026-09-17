// METU course codes are seven digits: a three-digit department code followed by
// a four-digit course number, so 5710213 is CENG 213 and 2402205 is HIST 2205.
export function courseNumber(code) {
  return String(code).slice(3).replace(/^0+(?=[0-9])/, "");
}
