import { apiUrl } from "@/lib/api/config";
import { getAccessToken } from "@/lib/auth/session";
import type {
  AdminPropertyCreate,
  AdminPropertyUpdate,
} from "@/types/admin";
import type { Property as PropertyRead } from "@/types/property";

function formatErrorMessage(status: number, message: string): string {
  const normalizedMessage = message.trim();

  if (normalizedMessage.startsWith(`HTTP ${status}`)) {
    return normalizedMessage;
  }

  return `HTTP ${status}: ${normalizedMessage}`;
}

export class AdminApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(formatErrorMessage(status, message));
    this.name = "AdminApiError";
    this.status = status;
  }
}

function buildUrl(path: string): URL {
  return new URL(path, `${apiUrl.replace(/\/$/, "")}/`);
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new AdminApiError(401, "No active session");
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

async function getErrorMessage(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown; message?: unknown };
    const message = body.detail ?? body.message;

    if (typeof message === "string" && message.trim().length > 0) {
      return message;
    }
  } catch {
    // Fall through to a stable status-based message.
  }

  return res.statusText || `Request failed with status ${res.status}`;
}

async function request<T>(
  path: string,
  init: RequestInit,
): Promise<T> {
  const headers: HeadersInit = {
    ...(await getAuthHeaders()),
    ...(init.body ? { "Content-Type": "application/json" } : {}),
    ...init.headers,
  };

  const res = await fetch(buildUrl(path), {
    ...init,
    headers,
  });

  if (!res.ok) {
    throw new AdminApiError(res.status, await getErrorMessage(res));
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export async function createProperty(
  data: AdminPropertyCreate,
): Promise<PropertyRead> {
  return request<PropertyRead>("/api/v1/admin/properties", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateProperty(
  id: string,
  data: AdminPropertyUpdate,
): Promise<PropertyRead> {
  return request<PropertyRead>(
    `/api/v1/admin/properties/${encodeURIComponent(id)}`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  );
}

export async function deleteProperty(id: string): Promise<void> {
  await request<void>(`/api/v1/admin/properties/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}

export const adminApi = {
  createProperty,
  updateProperty,
  deleteProperty,
};
