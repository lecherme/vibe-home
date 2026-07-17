import path from "node:path";
import { mkdir } from "node:fs/promises";
import { config as loadEnv } from "dotenv";
import {
  chromium,
  expect,
  request,
  test as base,
  type APIRequestContext,
  type Browser,
  type BrowserContext,
  type FullConfig,
  type Page,
} from "@playwright/test";

type AuthFixtures = {
  guestPage: Page;
  userPage: Page;
  adminPage: Page;
};

type LoginTarget = {
  email: string;
  password: string;
  expectedPath: string;
  storageStatePath: string;
};

const authDirectory = path.resolve(process.cwd(), ".auth");
const userStorageStatePath = path.join(authDirectory, "user.json");
const adminStorageStatePath = path.join(authDirectory, "admin.json");
const frontendEnvPath = path.resolve(process.cwd(), "../frontend/.env");
const localBackendOrigin = process.env.PLAYWRIGHT_BACKEND_ORIGIN ?? "http://localhost:8000";

loadEnv({ path: frontendEnvPath, override: false });

function getOrigin(value: string | undefined): string | null {
  if (!value) {
    return null;
  }

  try {
    return new URL(value).origin;
  } catch {
    return null;
  }
}

const configuredFrontendApiOrigin = getOrigin(process.env.NEXT_PUBLIC_API_URL);

function requireEnv(name: string): string {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

async function attachBackendProxy(context: BrowserContext): Promise<APIRequestContext | null> {
  if (!configuredFrontendApiOrigin || configuredFrontendApiOrigin === localBackendOrigin) {
    return null;
  }

  const api = await request.newContext();

  await context.route(`${configuredFrontendApiOrigin}/**`, async (route) => {
    try {
      const originalRequest = route.request();
      const rewrittenUrl = originalRequest
        .url()
        .replace(configuredFrontendApiOrigin, localBackendOrigin);

      // SSE streaming endpoints must not be buffered: route.fulfill buffers the
      // entire body before delivery, collapsing all React state transitions into
      // one batch so intermediate stage messages never render.  Using
      // route.continue with a URL override lets the browser handle the stream
      // natively, preserving each chunk as it arrives.
      if (rewrittenUrl.includes("/api/v1/search/ai/stream")) {
        await route.continue({ url: rewrittenUrl });
        return;
      }

      const headers = await originalRequest.allHeaders();

      delete headers.host;
      delete headers.origin;
      delete headers.referer;
      delete headers["content-length"];

      const response = await api.fetch(rewrittenUrl, {
        method: originalRequest.method(),
        headers,
        data: originalRequest.postDataBuffer() ?? undefined,
        timeout: 60_000,
      });

      await route.fulfill({
        status: response.status(),
        headers: response.headers(),
        body: await response.body(),
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);

      if (/Target page, context or browser has been closed|Request context disposed/i.test(message)) {
        await route.abort().catch(() => undefined);
        return;
      }

      throw error;
    }
  });

  return api;
}

async function closeContextWithProxy(
  context: BrowserContext,
  api: APIRequestContext | null,
): Promise<void> {
  if (api) {
    await context.unrouteAll({ behavior: "ignoreErrors" }).catch(() => undefined);
  }

  await context.close();

  if (api) {
    await api.dispose();
  }
}

export async function waitForAppReady(page: Page): Promise<void> {
  await page.waitForLoadState("domcontentloaded");
  await page.waitForLoadState("networkidle", { timeout: 10_000 }).catch(() => undefined);
}

export async function gotoAndWait(page: Page, url: string): Promise<void> {
  await page.goto(url);
  await waitForAppReady(page);
}

async function loginViaFrontend(
  browser: Browser,
  baseURL: string,
  target: LoginTarget,
): Promise<void> {
  const context = await browser.newContext();
  const api = await attachBackendProxy(context);
  const page = await context.newPage();

  try {
    await page.goto(new URL("/login", baseURL).toString());
    await waitForAppReady(page);
    await page.getByLabel("Email address").fill(target.email);
    await page.getByLabel("Password").fill(target.password);

    await Promise.all([
      page.waitForURL((url) => url.pathname !== "/login", { timeout: 15000 }),
      page.getByRole("button", { name: "Sign in" }).click(),
    ]);

    await expect(page).toHaveURL(new RegExp(`${target.expectedPath.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?:\\?|$)`));
    await page.context().storageState({ path: target.storageStatePath });
  } finally {
    await closeContextWithProxy(context, api);
  }
}

export default async function globalSetup(config: FullConfig): Promise<void> {
  const projectUse = config.projects[0]?.use ?? {};
  const configuredBaseURL = projectUse.baseURL;
  const baseURL =
    (typeof configuredBaseURL === "string" && configuredBaseURL) ||
    process.env.PLAYWRIGHT_BASE_URL ||
    "http://localhost:3000";

  await mkdir(authDirectory, { recursive: true });

  const browser = await chromium.launch();

  try {
    await loginViaFrontend(browser, baseURL, {
      email: requireEnv("TEST_USER_EMAIL"),
      password: requireEnv("TEST_USER_PASSWORD"),
      expectedPath: "/properties",
      storageStatePath: userStorageStatePath,
    });

    await loginViaFrontend(browser, baseURL, {
      email: requireEnv("TEST_ADMIN_EMAIL"),
      password: requireEnv("TEST_ADMIN_PASSWORD"),
      expectedPath: "/admin/properties",
      storageStatePath: adminStorageStatePath,
    });
  } finally {
    await browser.close();
  }
}

export const test = base.extend<AuthFixtures>({
  guestPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const api = await attachBackendProxy(context);
    const page = await context.newPage();

    try {
      await use(page);
    } finally {
      await closeContextWithProxy(context, api);
    }
  },
  userPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: userStorageStatePath,
    });
    const api = await attachBackendProxy(context);
    const page = await context.newPage();

    try {
      await use(page);
    } finally {
      await closeContextWithProxy(context, api);
    }
  },
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: adminStorageStatePath,
    });
    const api = await attachBackendProxy(context);
    const page = await context.newPage();

    try {
      await use(page);
    } finally {
      await closeContextWithProxy(context, api);
    }
  },
});

export { expect };
