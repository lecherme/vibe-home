import type { Page } from "@playwright/test";
import { expect, gotoAndWait, test } from "../fixtures/auth";

function adminTableRows(page: Page) {
  return page.locator("tbody tr");
}

async function fillPropertyForm(
  page: Page,
  values: {
    title: string;
    description: string;
    price: string;
    location: string;
    bedrooms: string;
    bathrooms: string;
    area: string;
  },
): Promise<void> {
  await page.getByLabel("Title").fill(values.title);
  await page.getByLabel("Description").fill(values.description);
  await page.getByLabel("Price ($)").fill(values.price);
  await page.getByLabel("Location").fill(values.location);
  await page.getByLabel("Bedrooms").fill(values.bedrooms);
  await page.getByLabel("Bathrooms").fill(values.bathrooms);
  await page.getByLabel("Area (sqm)").fill(values.area);
}

test.describe("admin", () => {
  test("blocks non-admin access to /admin/properties", async ({ userPage }) => {
    await gotoAndWait(userPage, "/admin/properties");

    // Regardless of whether the app redirects or returns a 403 page,
    // the admin property table must not be rendered.
    await expect(userPage.getByRole("table")).toHaveCount(0);
    await expect(userPage.getByRole("heading", { name: /manage properties/i })).toHaveCount(0);
    await expect(userPage).not.toHaveURL(/\/admin\/properties(?:\?|$)/);
  });

  test("allows an admin to access property management and perform create/edit/delete on a test-owned property", async ({
    adminPage,
  }) => {
    test.setTimeout(120_000);

    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const createdTitle = `E2E Test Property ${timestamp}`;
    const updatedTitle = `${createdTitle} Updated`;

    await gotoAndWait(adminPage, "/admin/properties");
    await expect(adminPage.getByRole("heading", { name: /manage properties/i })).toBeVisible();
    await expect(adminPage.getByRole("link", { name: /add property/i })).toBeVisible({
      timeout: 30_000,
    });
    await expect(adminPage.getByRole("table")).toBeVisible({ timeout: 30_000 });

    await adminPage.getByRole("link", { name: /add property/i }).click();
    await expect(adminPage).toHaveURL(/\/admin\/properties\/new$/, { timeout: 30_000 });
    await expect(adminPage.getByRole("heading", { name: /add new property/i })).toBeVisible();

    await fillPropertyForm(adminPage, {
      title: createdTitle,
      description: "Created by the Playwright E2E suite for admin CRUD coverage.",
      price: "7654321",
      location: "Central, Hong Kong",
      bedrooms: "2",
      bathrooms: "2",
      area: "68",
    });

    await adminPage.getByRole("button", { name: /save property/i }).click();
    await expect(adminPage).toHaveURL(/\/admin\/properties(?:\?|$)/, { timeout: 30_000 });

    const createdRow = adminTableRows(adminPage).filter({ hasText: createdTitle }).first();
    await expect(createdRow).toBeVisible({ timeout: 30_000 });

    await createdRow.getByRole("link", { name: /^edit$/i }).click();
    await expect(adminPage).toHaveURL(/\/admin\/properties\/[^/]+\/edit$/, { timeout: 30_000 });
    await expect(adminPage.getByRole("heading", { name: /edit property/i })).toBeVisible();

    await adminPage.getByLabel("Title").fill(updatedTitle);
    await adminPage.getByRole("button", { name: /save property/i }).click();
    await expect(adminPage).toHaveURL(/\/admin\/properties(?:\?|$)/, { timeout: 30_000 });

    const updatedRow = adminTableRows(adminPage).filter({ hasText: updatedTitle }).first();
    await expect(updatedRow).toBeVisible({ timeout: 30_000 });

    await updatedRow.getByRole("button", { name: /^delete$/i }).click();
    await updatedRow.getByRole("button", { name: /^yes$/i }).click();

    await expect(adminTableRows(adminPage).filter({ hasText: updatedTitle })).toHaveCount(0);
  });
});
