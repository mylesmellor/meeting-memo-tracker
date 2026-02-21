/**
 * E2E tests for authentication flows.
 *
 * Requires the full stack running with seeded data:
 *   make up && make migrate && make seed
 *
 * Demo credentials (from seed_demo.py):
 *   alice@acme-demo.com / demo1234
 */
import { expect, test } from "@playwright/test";

const DEMO_EMAIL = "alice@acme-demo.com";
const DEMO_PASSWORD = "demo1234";

test.describe("Authentication", () => {
  test("unauthenticated visit to /dashboard redirects to /auth/login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test("login with demo credentials lands on dashboard", async ({ page }) => {
    await page.goto("/auth/login");

    await page.getByLabel(/email/i).fill(DEMO_EMAIL);
    await page.getByLabel(/password/i).fill(DEMO_PASSWORD);
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });
  });

  test("logout redirects to login page", async ({ page }) => {
    // Log in first
    await page.goto("/auth/login");
    await page.getByLabel(/email/i).fill(DEMO_EMAIL);
    await page.getByLabel(/password/i).fill(DEMO_PASSWORD);
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });

    // Find and click the logout button (typically in nav/sidebar)
    await page.getByRole("button", { name: /logout|sign out/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10_000 });
  });

  test("register flow creates account and lands on dashboard", async ({ page }) => {
    await page.goto("/auth/register");

    // Use a unique email so the test is idempotent on re-runs
    const uniqueEmail = `e2e-test-${Date.now()}@example.com`;

    await page.getByLabel(/full name|name/i).fill("E2E Test User");
    await page.getByLabel(/email/i).fill(uniqueEmail);
    await page.getByLabel(/password/i).fill("securepass123");
    // Some register forms have an org name field
    const orgField = page.getByLabel(/organisation|organization|org/i);
    if (await orgField.isVisible()) {
      await orgField.fill("E2E Test Org");
    }

    await page.getByRole("button", { name: /register|create account|sign up/i }).click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });
  });

  test("invalid credentials shows error message", async ({ page }) => {
    await page.goto("/auth/login");

    await page.getByLabel(/email/i).fill(DEMO_EMAIL);
    await page.getByLabel(/password/i).fill("wrong-password");
    await page.getByRole("button", { name: /sign in/i }).click();

    // Should stay on login page and show an error
    await expect(page).toHaveURL(/\/auth\/login/);
    await expect(page.getByText(/invalid|incorrect|credentials/i)).toBeVisible({ timeout: 5_000 });
  });
});
