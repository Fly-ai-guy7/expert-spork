import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config — E2E against a local backend + frontend.
 *
 * CI bootstrap: bring up docker-compose (db + redis + backend + worker +
 * frontend), wait for /readyz to return 200, then run these specs. Local:
 * `make dev` and `npx playwright test`.
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false, // tests share DB state
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: process.env.CI ? [["html", { open: "never" }], ["github"]] : "list",
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
});
