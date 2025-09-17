export function convertTime(day, hour, min) {
  const baseDate = new Date(2021, 1, 14);
  baseDate.setDate(baseDate.getDate() + day);
  baseDate.setHours(hour, min, 0, 0);

  return baseDate;
}
