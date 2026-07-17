import type { Page } from "@playwright/test";
import { expect, gotoAndWait, test, waitForAppReady } from "../fixtures/auth";

function requireEnv(name: string): string {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

async function submitLoginForm(
  page: Page,
  options?: { redirectTo?: string; password?: string },
): Promise<void> {
  const email = requireEnv("TEST_USER_EMAIL");
  const password = options?.password ?? requireEnv("TEST_USER_PASSWORD");
  const redirectTo = options?.redirectTo;
  const loginUrl = redirectTo
    ? `/login?redirectTo=${encodeURIComponent(redirectTo)}`
    : "/login";

  await gotoAndWait(page, loginUrl);
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
}

test.describe("auth and route protection", () => {
  test("redirects unauthenticated users from /properties to /login", async ({
    guestPage,
  }) => {
    await guestPage.goto("/properties");

    await expect(guestPage).toHaveURL(/\/login(?:\?|$)/);
    await expect(guestPage.getByRole("heading", { name: /sign in to your account/i })).toBeVisible();
  });

  test("redirects unauthenticated users from /favorites to /login", async ({
    guestPage,
  }) => {
    await guestPage.goto("/favorites");

    await expect(guestPage).toHaveURL(/\/login(?:\?|$)/);
    await expect(guestPage.getByRole("heading", { name: /sign in to your account/i })).toBeVisible();
  });

  test("logs in successfully and redirects to /properties by default", async ({
    guestPage,
  }) => {
    await submitLoginForm(guestPage);

    await expect(guestPage).toHaveURL(/\/properties(?:\?|$)/, { timeout: 15_000 });
    await expect(guestPage.getByRole("heading", { name: /^properties$/i })).toBeVisible();
  });

  test("logs in successfully and respects redirectTo", async ({ guestPage }) => {
    await submitLoginForm(guestPage, { redirectTo: "/favorites" });

    await expect(guestPage).toHaveURL(/\/favorites(?:\?|$)/, { timeout: 15_000 });
    await expect(guestPage.getByRole("heading", { name: /my favorites/i })).toBeVisible();
  });

  test("shows an error and keeps the form usable on login failure", async ({
    guestPage,
  }) => {
    await submitLoginForm(guestPage, { password: "DefinitelyWrongPassword123" });

    await expect(guestPage).toHaveURL(/\/login(?:\?|$)/, { timeout: 15_000 });
    await expect(
      guestPage.locator("div.rounded-md.bg-red-50").filter({
        hasText: /invalid|credential|password|email/i,
      }),
    ).toBeVisible({ timeout: 15_000 });
    await expect(guestPage.getByLabel("Email address")).toBeEnabled();
    await expect(guestPage.getByLabel("Password")).toBeEnabled();
    await expect(guestPage.getByRole("button", { name: "Sign in" })).toBeVisible();
  });

  test("logs out and returns to /login", async ({ userPage }) => {
    await gotoAndWait(userPage, "/properties");
    await Promise.all([
      userPage.waitForURL(/\/login(?:\?|$)/, { timeout: 15_000 }),
      userPage.getByRole("button", { name: /sign out/i }).click(),
    ]);

    await expect(userPage).toHaveURL(/\/login(?:\?|$)/, { timeout: 15_000 });
    await expect(userPage.getByRole("heading", { name: /sign in to your account/i })).toBeVisible();
  });

  test("redirects authenticated users away from /login", async ({ userPage }) => {
    await userPage.goto("/login");

    await expect(userPage).toHaveURL(/\/properties(?:\?|$)/);
    await expect(userPage).not.toHaveURL(/\/login(?:\?|$)/);
  });

  test("redirects authenticated users away from /register", async ({ userPage }) => {
    await userPage.goto("/register");

    await expect(userPage).toHaveURL(/\/properties(?:\?|$)/);
    await expect(userPage).not.toHaveURL(/\/register(?:\?|$)/);
  });

  test("register page renders form and rejects mismatched passwords without submitting", async ({
    guestPage,
  }) => {
    await gotoAndWait(guestPage, "/register");

    await expect(guestPage.getByLabel("Email address")).toBeVisible();
    await expect(guestPage.getByLabel(/^password$/i)).toBeVisible();
    await expect(guestPage.getByLabel("Confirm Password")).toBeVisible();
    await expect(guestPage.getByRole("button", { name: /^register$/i })).toBeVisible();

    // password mismatch is rejected client-side — no Supabase account is created
    await guestPage.getByLabel("Email address").fill("test@example.com");
    await guestPage.getByLabel(/^password$/i).fill("Password123");
    await guestPage.getByLabel("Confirm Password").fill("Different456");
    await guestPage.getByRole("button", { name: /^register$/i }).click();

    await expect(guestPage).toHaveURL(/\/register(?:\?|$)/);
    await expect(guestPage).not.toHaveURL(/\/properties(?:\?|$)/);
    expect(guestPage.url()).not.toContain("email=");
    expect(guestPage.url()).not.toContain("password=");
  });

  test("does not expose login credentials in the URL after submit", async ({
    guestPage,
  }) => {
    await submitLoginForm(guestPage, { redirectTo: "/properties" });

    await expect(guestPage).toHaveURL(/\/properties(?:\?|$)/, { timeout: 15_000 });
    await waitForAppReady(guestPage);

    const currentUrl = new URL(guestPage.url());
    expect(currentUrl.search).not.toContain("email=");
    expect(currentUrl.search).not.toContain("password=");
  });
});
