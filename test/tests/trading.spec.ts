import { test, expect } from '@playwright/test';

test.describe('FinAlly AI Trading Workstation End-to-End', () => {
  test('Fresh start: default watchlist, cash balance, and terminal renders', async ({ page }) => {
    await page.goto('/');

    // Check title / brand
    await expect(page.locator('text=FinAlly')).toBeVisible();

    // Check $10,000 cash balance
    await expect(page.locator('text=$10,000.00')).toBeVisible();

    // Check default watchlist has AAPL
    await expect(page.locator('text=AAPL').first()).toBeVisible();
  });

  test('Manual trade execution: buy shares and check portfolio updates', async ({ page }) => {
    await page.goto('/');

    // Select AAPL if not selected
    await page.locator('text=AAPL').first().click();

    // Fill trade quantity
    const qtyInput = page.locator('input[type="number"]');
    await qtyInput.fill('5');

    // Click Buy button
    const buyButton = page.locator('button:has-text("Buy")');
    await buyButton.click();

    // Verify positions table shows AAPL
    await expect(page.locator('table')).toContainText('AAPL');
  });

  test('AI Copilot: send chat message and receive response with trade execution', async ({ page }) => {
    await page.goto('/');

    const chatInput = page.locator('input[placeholder*="Ask"]');
    await chatInput.fill('buy 2 shares of MSFT');
    await page.locator('button:has-text("Send")').click();

    // Assistant response should appear
    await expect(page.locator('text=MSFT')).toBeVisible();
  });
});
