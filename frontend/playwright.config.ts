import { defineConfig, devices } from '@playwright/test'
import { defineBddConfig } from 'playwright-bdd'

// Generiert Playwright-Testdateien aus den Gherkin-Features (playwright-bdd).
const testDir = defineBddConfig({
  features: 'e2e/features/**/*.feature',
  steps: 'e2e/steps/**/*.ts',
})

const PORT = 5173
const baseURL = `http://localhost:${PORT}`

// Teststrategie (ADR-013): E2E bleibt schlank – nur kritische Smoke-Journeys.
export default defineConfig({
  testDir,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  use: {
    baseURL,
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  // Dev-Server für den Smoke-Test (kein Build nötig).
  webServer: {
    command: `npm run dev -- --port ${PORT} --strictPort`,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
})
