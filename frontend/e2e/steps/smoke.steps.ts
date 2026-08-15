import { expect } from '@playwright/test'
import { createBdd } from 'playwright-bdd'

const { Given, Then } = createBdd()

Given('die Anwendung ist geöffnet', async ({ page }) => {
  await page.goto('/')
})

Then('sehe ich den Titel {string}', async ({ page }, titel: string) => {
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(titel)
})
