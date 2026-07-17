import { expect, gotoAndWait, test } from "../fixtures/auth";
import type { Page } from "@playwright/test";

async function expectSearchOutcome(page: Page): Promise<void> {
  await expect(
    page.locator("text=/Found\\s+\\d+\\s+properties/i").or(
      page.getByText(/no properties found matching your criteria/i),
    ),
  ).toBeVisible({ timeout: 15_000 });
}

async function waitForFilterSearchReady(page: Page): Promise<void> {
  await expect(page.getByPlaceholder(/search by location/i)).toBeEnabled({
    timeout: 60_000,
  });

  const searchButton = page.getByRole("button", { name: /^search$/i });

  await expect(searchButton).toBeVisible({ timeout: 60_000 });
  await expect(searchButton).toBeEnabled({ timeout: 60_000 });
}


test.describe("search", () => {
  test("loads the search page without error", async ({ userPage }) => {
    await gotoAndWait(userPage, "/search");
    await waitForFilterSearchReady(userPage);

    await expect(userPage.getByRole("heading", { name: /search properties/i })).toBeVisible();
    await expect(userPage.getByRole("button", { name: /ai search/i })).toBeVisible();
  });

  test("supports a location filter search", async ({ userPage }) => {
    await gotoAndWait(userPage, "/search");
    await waitForFilterSearchReady(userPage);
    await userPage.getByPlaceholder(/search by location/i).fill("North Point");
    await userPage.getByRole("button", { name: /^search$/i }).click();

    await expect(userPage).toHaveURL(/\/search\?[^#]*location=North(\+|%20)Point/, {
      timeout: 15_000,
    });
    await expectSearchOutcome(userPage);
  });

  test("writes min and max price filters into the URL", async ({ userPage }) => {
    await gotoAndWait(userPage, "/search");
    await waitForFilterSearchReady(userPage);
    await userPage.getByLabel("Min Price").fill("5000000");
    await userPage.getByLabel("Max Price").fill("10000000");

    await expect.poll(() => new URL(userPage.url()).searchParams.get("min_price")).toBe("5000000");
    await expect.poll(() => new URL(userPage.url()).searchParams.get("max_price")).toBe("10000000");
  });

  test("clearing filters resets the URL and results state", async ({ userPage }) => {
    test.setTimeout(60_000);

    await gotoAndWait(userPage, "/search");
    await waitForFilterSearchReady(userPage);
    await userPage.getByPlaceholder(/search by location/i).fill("North Point");
    await userPage.getByRole("button", { name: /^search$/i }).click();
    await expect(userPage).toHaveURL(/location=North(\+|%20)Point/, {
      timeout: 15_000,
    });
    await expectSearchOutcome(userPage);

    const clearFiltersButton = userPage.getByRole("button", { name: /clear filters/i });
    await expect(clearFiltersButton).toBeEnabled({ timeout: 30_000 });
    await clearFiltersButton.click();

    await expect(userPage).toHaveURL(/\/search$/, { timeout: 15_000 });
    await expect(userPage.getByPlaceholder(/search by location/i)).toHaveValue("");
    await expectSearchOutcome(userPage);
  });

  test("streams the AI search stages in order without console errors", async ({
    userPage,
  }) => {
    test.setTimeout(120_000);

    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    userPage.on("console", (message) => {
      if (
        message.type() === "error" &&
        !/ERR_CONNECTION_RESET|ERR_ABORTED/i.test(message.text())
      ) {
        consoleErrors.push(message.text());
      }
    });
    userPage.on("pageerror", (error) => {
      pageErrors.push(error.message);
    });

    await gotoAndWait(userPage, "/search");
    await waitForFilterSearchReady(userPage);
    await userPage.getByRole("button", { name: /ai search/i }).click();
    await expect(
      userPage.getByPlaceholder(/describe the property you are looking for/i),
    ).toBeVisible({ timeout: 15_000 });
    await userPage
      .getByPlaceholder(/describe the property you are looking for/i)
      .fill("2 bedroom apartment in North Point");
    await userPage
      .getByPlaceholder(/describe the property you are looking for/i)
      .press("Enter");

    // Each assertion waits for the stage indicator to become visible.
    // Stages are sequential and each depends on an LLM or DB call (≥1 s),
    // so there is no race between the assertion and the transition.

    // 1. parsing — LLM interprets the query
    await expect(userPage.getByText("理解搜索语义中...")).toBeVisible({ timeout: 30_000 });

    // 2. searching — DB retrieves matching properties
    await expect(userPage.getByText("检索匹配房源中...")).toBeVisible({ timeout: 30_000 });

    // 3. results — property cards rendered
    await expect(userPage.locator("text=/Found\\s+\\d+\\s+properties/i")).toBeVisible({
      timeout: 60_000,
    });
    await expect(
      userPage
        .locator('a[href^="/properties/"]')
        .filter({ has: userPage.locator("h3") })
        .first(),
    ).toBeVisible({ timeout: 60_000 });

    // 4. summarizing — LLM generates summary
    await expect(userPage.getByText("生成摘要中...")).toBeVisible({ timeout: 30_000 });

    // 5. summary — final AI summary rendered
    await expect(userPage.getByRole("heading", { name: /ai summary/i })).toBeVisible({
      timeout: 60_000,
    });
    await expect(
      userPage
        .locator("section")
        .filter({ has: userPage.getByRole("heading", { name: /ai summary/i }) })
        .locator("p"),
    ).toBeVisible({ timeout: 60_000 });

    expect(consoleErrors).toEqual([]);
    expect(pageErrors).toEqual([]);
  });
});
