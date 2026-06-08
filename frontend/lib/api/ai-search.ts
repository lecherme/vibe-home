import { apiUrl } from "@/lib/api/config";
import { getAccessToken } from "@/lib/auth/session";
import type { AiSearchRequest, AiSearchResult } from "@/types/search";

export class AiSearchApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    const normalizedMessage = message.trim();
    const finalMessage = normalizedMessage.startsWith(`HTTP ${status}`)
      ? normalizedMessage
      : `HTTP ${status}: ${normalizedMessage}`;
      
    super(finalMessage);
    this.name = "AiSearchApiError";
    this.status = status;
  }
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new AiSearchApiError(401, "No active session");
  }

  return {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
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
    // Fall through
  }

  return res.statusText || `Request failed with status ${res.status}`;
}

export async function aiSearch(
  query: string,
  page = 1,
  pageSize = 20
): Promise<AiSearchResult> {
  const url = new URL("/api/v1/search/ai", `${apiUrl.replace(/\/$/, "")}/`);

  const reqBody: AiSearchRequest = {
    query,
    page,
    page_size: pageSize,
  };

  const res = await fetch(url, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify(reqBody),
  });

  if (!res.ok) {
    throw new AiSearchApiError(res.status, await getErrorMessage(res));
  }

  return res.json() as Promise<AiSearchResult>;
}
