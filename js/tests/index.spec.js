import { test, expect } from "@playwright/test";

test.describe("Basics", () => {
  test("basic", async ({ page }) => {
    await expect("").toBe("");
  });
});
