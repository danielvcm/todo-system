import { test, expect } from '@playwright/test';

test('Due Today flow renders the panel shell', async ({ page }) => {
  await page.goto('http://127.0.0.1:4173/');
  await expect(page.getByRole('heading', { name: /due today/i })).toBeVisible();
  await expect(page.getByRole('link', { name: /create task/i })).toBeVisible();
});
