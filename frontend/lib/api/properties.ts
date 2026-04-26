import { getAccessToken } from "@/lib/auth/session";
import type { Property, PropertyListResponse } from "@/types/property";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class PropertyApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "PropertyApiError";
    this.status = status;
  }
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new PropertyApiError(401, "No active session");
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

function buildUrl(path: string): URL {
  return new URL(path, `${apiUrl.replace(/\/$/, "")}/`);
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

async function request<T>(url: URL): Promise<T> {
  const res = await fetch(url, {
    headers: await getAuthHeaders(),
  });

  if (!res.ok) {
    throw new PropertyApiError(res.status, await getErrorMessage(res));
  }

  return res.json() as Promise<T>;
}

async function list(
  page: number,
  pageSize: number,
): Promise<PropertyListResponse> {
  const url = buildUrl("/api/v1/properties");
  url.searchParams.set("page", String(page));
  url.searchParams.set("page_size", String(pageSize));

  return request<PropertyListResponse>(url);
}

async function get(id: string): Promise<Property> {
  return request<Property>(buildUrl(`/api/v1/properties/${encodeURIComponent(id)}`));
}

export const propertiesApi = {
  list,
  get,
};
