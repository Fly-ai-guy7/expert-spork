import { test, expect } from "@playwright/test";

/**
 * Trainee golden path: register → AI-generate a practice case → run →
 * download the ruling PDF + coaching report. Each step is its own test so
 * a failure points at the broken stage rather than the whole flow.
 *
 * Hits the API directly to register (no signup UI yet) and exercises the
 * SPA for the run + view flow.
 */

const API = process.env.E2E_API_BASE || "http://localhost:8000";
const EMAIL = `e2e+${Date.now()}@example.com`;
const PASSWORD = "correct-horse-battery";

let token = "";
let caseId = "";

test.beforeAll(async ({ request }) => {
  const r = await request.post(`${API}/api/v1/auth/register`, {
    data: { email: EMAIL, password: PASSWORD, organization_name: "E2E Org" },
  });
  expect(r.ok()).toBeTruthy();
  token = (await r.json()).access_token;
});

test("disclaimer banner is non-removable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText(/AI Simulation Only/i)).toBeVisible();
});

test("AR/EN toggle flips dir", async ({ page }) => {
  await page.goto("/");
  const html = page.locator("html");
  await expect(html).toHaveAttribute("dir", "ltr");
  await page.getByRole("button", { name: /العربية|Arabic/i }).click();
  await expect(html).toHaveAttribute("dir", "rtl");
});

test("generate practice case via API and view it in the SPA", async ({ page, request }) => {
  const r = await request.post(`${API}/api/v1/cases/generate`, {
    headers: { Authorization: `Bearer ${token}` },
    data: { area_of_law: "IP", difficulty: 2, language: "en" },
  });
  expect(r.ok()).toBeTruthy();
  caseId = (await r.json()).id;

  await page.goto(`/cases/${caseId}`);
  await expect(page.getByText(/ALPHA|trademark|case/i)).toBeVisible({ timeout: 15_000 });
});

test("run the simulation and reach a ruling", async ({ page, request }) => {
  await request.post(`${API}/api/v1/cases/${caseId}/run`, {
    headers: { Authorization: `Bearer ${token}` },
    data: { max_rounds: 1 },
  });
  await page.goto(`/cases/${caseId}`);
  // Live status (SSE) should transition to COMPLETE within the LLM call budget.
  await expect(page.getByText(/COMPLETE|Ruling/i)).toBeVisible({ timeout: 90_000 });
});

test("download the ruling PDF", async ({ request }) => {
  const r = await request.get(`${API}/api/v1/cases/${caseId}/report.pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(r.ok()).toBeTruthy();
  expect(r.headers()["content-type"]).toContain("application/pdf");
  const body = await r.body();
  expect(body.subarray(0, 4).toString()).toBe("%PDF");
});
