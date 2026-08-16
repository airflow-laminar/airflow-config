import { test, expect } from "@playwright/test";

test.describe("Basics", () => {
  test("basic", async () => {
    await expect("").toBe("");
  });
});
