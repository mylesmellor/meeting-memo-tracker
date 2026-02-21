/**
 * Playwright E2E configuration.
 *
 * Prerequisites — the full Docker stack must be running with seeded data:
 *
 *   make up && make migrate && make seed
 *
 * Then run:
 *
 *   make test-e2e
 *   # or: cd apps/web && npx playwright test
 */
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: "list",

  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  // Assumes the stack is already running via `make up`.
  // reuseExistingServer: true prevents Playwright from trying to start the app.
  webServer: {
    command: "echo 'Assuming docker stack is running. Run: make up && make migrate && make seed'",
    url: "http://localhost:3000",
    reuseExistingServer: true,
    timeout: 15_000,
  },
});
