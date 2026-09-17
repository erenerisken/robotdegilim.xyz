import { afterEach, describe, expect, it, vi } from "vitest";
import { withDeadline } from "./withDeadline";

afterEach(() => vi.useRealTimers());

describe("withDeadline", () => {
  it("passes a value through when it arrives in time", async () => {
    await expect(withDeadline(Promise.resolve("courses"), 1000)).resolves.toBe(
      "courses"
    );
  });

  it("passes a rejection through untouched", async () => {
    await expect(
      withDeadline(Promise.reject(new Error("offline")), 1000)
    ).rejects.toThrow("offline");
  });

  it("rejects a promise that never settles", async () => {
    vi.useFakeTimers();
    const pending = withDeadline(new Promise(() => {}), 35000, "Timed out");
    const settled = expect(pending).rejects.toThrow("Timed out");

    await vi.advanceTimersByTimeAsync(35000);
    await settled;
  });

  it("does not leave its timer running once the promise settles", async () => {
    vi.useFakeTimers();
    await withDeadline(Promise.resolve("courses"), 35000);

    expect(vi.getTimerCount()).toBe(0);
  });
});
