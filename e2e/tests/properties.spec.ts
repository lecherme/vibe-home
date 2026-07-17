import type { Page } from "@playwright/test";
import { expect, gotoAndWait, test } from "../fixtures/auth";

function propertyContentLinks(page: Page) {
  return page.locator('a[href^="/properties/"]').filter({
    has: page.locator("h3"),
  });
}

test.describe("properties", () => {
  test("renders property cards with title, price, and location", async ({
    userPage,
  }) => {
    await gotoAndWait(userPage, "/properties");

    await expect(userPage.getByRole("heading", { name: /^properties$/i })).toBeVisible();

    const firstCard = propertyContentLinks(userPage).first();
    await expect(firstCard).toBeVisible({ timeout: 30_000 });
    await expect(firstCard.locator("h3")).toBeVisible();
    await expect(firstCard.locator("span").filter({ hasText: /^\$/ }).first()).toBeVisible();
    await expect(firstCard.locator("p").first()).toBeVisible();
  });

  test("advances pagination when Next is available and enabled", async ({
    userPage,
  }) => {
    await gotoAndWait(userPage, "/properties");

    const nextButton = userPage.getByRole("button", { name: /^next$/i });

    if ((await nextButton.count()) === 0) {
      return;
    }

    if (await nextButton.isDisabled()) {
      await expect(nextButton).toBeDisabled();
      return;
    }

    await Promise.all([
      userPage.waitForURL(/\/properties\?page=2$/, { timeout: 30_000 }),
      nextButton.click(),
    ]);
  });

  test("navigates to a property detail page when a card is clicked", async ({
    userPage,
  }) => {
    await gotoAndWait(userPage, "/properties");

    const firstCard = propertyContentLinks(userPage).first();
    await expect(firstCard).toBeVisible({ timeout: 30_000 });
    const expectedTitle = (await firstCard.locator("h3").innerText()).trim();

    await Promise.all([
      userPage.waitForURL(/\/properties\/[^/?#]+$/, { timeout: 30_000 }),
      firstCard.click(),
    ]);

    await expect(userPage).toHaveURL(/\/properties\/[^/?#]+$/);
    await expect(userPage.getByRole("heading", { name: expectedTitle })).toBeVisible();
  });

  test("loads property details directly and shows the property title", async ({
    userPage,
  }) => {
    await gotoAndWait(userPage, "/properties");

    const firstCard = propertyContentLinks(userPage).first();
    await expect(firstCard).toBeVisible({ timeout: 30_000 });
    const detailHref = await firstCard.getAttribute("href");
    const expectedTitle = (await firstCard.locator("h3").innerText()).trim();

    expect(detailHref).toBeTruthy();

    await userPage.goto(detailHref!);

    await expect(userPage).toHaveURL(/\/properties\/[^/?#]+$/);
    await expect(userPage.getByRole("heading", { name: expectedTitle })).toBeVisible();
    await expect(userPage.getByText(/^price$/i)).toBeVisible();
    await expect(userPage.getByText(/^description$/i)).toBeVisible();
  });
});
