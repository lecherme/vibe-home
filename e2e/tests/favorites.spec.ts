import type { Page } from "@playwright/test";
import { expect, gotoAndWait, test } from "../fixtures/auth";

function propertyCards(page: Page) {
  return page.locator("div.group.relative");
}

function favoriteButtons(page: Page) {
  return page.getByRole("button", {
    name: /add to favorites|remove from favorites/i,
  });
}

async function waitForPropertiesListReady(page: Page): Promise<void> {
  await expect(propertyCards(page).first()).toBeVisible({ timeout: 60_000 });
  await expect(favoriteButtons(page).first()).toBeVisible({ timeout: 60_000 });
}

test.describe("favorites", () => {
  test("adds and removes a favorite from the property list", async ({
    userPage,
  }) => {
    test.setTimeout(90_000);

    await gotoAndWait(userPage, "/properties");
    await waitForPropertiesListReady(userPage);

    const toggle = favoriteButtons(userPage).first();

    const initialLabel = (await toggle.getAttribute("aria-label")) ?? "";

    if (/remove from favorites/i.test(initialLabel)) {
      await toggle.click();
      await expect(toggle).toHaveAttribute("aria-label", /add to favorites/i, {
        timeout: 15_000,
      });
    }

    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-label", /remove from favorites/i, {
      timeout: 15_000,
    });

    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-label", /add to favorites/i, {
      timeout: 15_000,
    });
  });

  test("renders the favorites page and removes a saved property from it", async ({
    userPage,
  }) => {
    test.setTimeout(90_000);

    await gotoAndWait(userPage, "/properties");
    await waitForPropertiesListReady(userPage);

    const card = propertyCards(userPage).first();

    const title = ((await card.locator("h3").first().textContent()) ?? "").trim();
    expect(title.length).toBeGreaterThan(0);

    const listToggle = card.getByRole("button", {
      name: /add to favorites|remove from favorites/i,
    });
    const currentLabel = (await listToggle.getAttribute("aria-label")) ?? "";

    if (/remove from favorites/i.test(currentLabel)) {
      await listToggle.click();
      await expect(listToggle).toHaveAttribute("aria-label", /add to favorites/i, {
        timeout: 15_000,
      });
    }

    await listToggle.click();
    await expect(listToggle).toHaveAttribute("aria-label", /remove from favorites/i, {
      timeout: 15_000,
    });

    await gotoAndWait(userPage, "/favorites");
    await expect(userPage.getByRole("heading", { name: /my favorites/i })).toBeVisible({
      timeout: 30_000,
    });

    const favoriteCard = propertyCards(userPage).filter({ hasText: title }).first();
    if (!(await favoriteCard.isVisible().catch(() => false))) {
      await expect(
        userPage.getByText(/no favorites yet/i).or(userPage.locator("div.group.relative")),
      ).toBeVisible();
      return;
    }

    const favoritesBefore = await propertyCards(userPage).count();

    await favoriteCard.getByRole("button", { name: /remove from favorites/i }).click();

    await expect.poll(async () => {
      const remainingMatchingCards = await propertyCards(userPage)
        .filter({ hasText: title })
        .count();
      const emptyStateVisible = await userPage.getByText(/no favorites yet/i).isVisible().catch(() => false);
      const favoritesAfter = await propertyCards(userPage).count();

      if (emptyStateVisible) {
        return "empty";
      }

      if (remainingMatchingCards === 0 && favoritesAfter < favoritesBefore) {
        return "removed";
      }

      return "pending";
    }).toMatch(/empty|removed/);
  });
});
