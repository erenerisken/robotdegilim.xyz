import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AddCourseWidget } from "./AddCourseWidget";

// Testing Library only unmounts by itself when vitest runs with globals.
afterEach(cleanup);

const course = (code, abbreviation, name) => ({
  code,
  abbreviation,
  name,
  sections: [],
});

// "EE: ADVANCED STUDIES" alone covers 59 of the real courses, so the catalogue
// is full of entries the old label could not tell apart.
const catalogue = [
  course(5670598, "EE", "ADVANCED STUDIES"),
  course(5670698, "EE", "ADVANCED STUDIES"),
  course(5710213, "CENG", "DATA STRUCTURES"),
  course(5710223, "CENG", "DISCRETE COMPUTATIONAL STRUCTURES"),
  course(2402205, "HIST", "HISTORY OF THE TURKISH REVOLUTION I"),
];

async function search(query) {
  const onCourseAdd = vi.fn();
  const user = userEvent.setup();
  render(<AddCourseWidget courses={catalogue} onCourseAdd={onCourseAdd} />);

  await user.click(screen.getByLabelText(/course name/i));
  if (query) await user.keyboard(query);

  return {
    user,
    onCourseAdd,
    options: () => screen.queryAllByRole("option").map((o) => o.textContent),
  };
}

describe("AddCourseWidget", () => {
  it("finds a course by its department and number", async () => {
    const { options } = await search("CENG 213");
    expect(options()).toEqual(["CENG 213: DATA STRUCTURES"]);
  });

  it("finds a course typed without a space", async () => {
    const { options } = await search("CENG213");
    expect(options()).toEqual(["CENG 213: DATA STRUCTURES"]);
  });

  it("finds a course by its seven-digit code", async () => {
    const { options } = await search("5710213");
    expect(options()).toEqual(["CENG 213: DATA STRUCTURES"]);
  });

  it("finds a course by part of its name", async () => {
    const { options } = await search("DATA STRUCT");
    expect(options()).toEqual(["CENG 213: DATA STRUCTURES"]);
  });

  it("keeps courses sharing a name apart", async () => {
    const { options } = await search("ADVANCED STUDIES");
    expect(options()).toEqual([
      "EE 598: ADVANCED STUDIES",
      "EE 698: ADVANCED STUDIES",
    ]);
  });

  it("adds the course that was picked", async () => {
    const { user, onCourseAdd } = await search("CENG 213");
    await user.click(screen.getByRole("option", { name: /DATA STRUCTURES/ }));

    expect(onCourseAdd).toHaveBeenCalledWith(
      expect.objectContaining({ code: 5710213 })
    );
  });

  it("clears the box so the next search starts fresh", async () => {
    const { user, options } = await search("CENG 213");
    await user.click(screen.getByRole("option", { name: /DATA STRUCTURES/ }));
    await user.click(screen.getByLabelText(/course name/i));
    await user.keyboard("HIST");

    expect(options()).toEqual([
      "HIST 2205: HISTORY OF THE TURKISH REVOLUTION I",
    ]);
  });
});
