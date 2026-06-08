import { apiUrl } from "@/lib/api/config";
import { getAccessToken } from "@/lib/auth/session";
import type { AiSearchResult } from "@/types/search";

export class AiSearchApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    const normalizedMessage = message.trim();
    const formattedMessage = normalizedMessage.startsWith(`HTTP ${status}`)
      ? normalizedMessage
      : `HTTP ${status}: ${normalizedMessage}`;
      
    super(formattedMessage);
    this.name = "AiSearchApiError";
    this.status = status;
  }
}

export async function aiSearch(
  query: string,
  page: number = 1,
  pageSize: number = 20
): Promise<AiSearchResult> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new AiSearchApiError(401, "No active session");
  }

  const url = new URL("/api/v1/search/ai", `${apiUrl.replace(/\/$/, "")}/`);
  
  const res = await fetch(url.toString(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      query,
      page,
      page_size: pageSize,
    }),
  });

  if (!res.ok) {
    let errorMessage = "AI Search failed";
    try {
      const body = (await res.json()) as { detail?: unknown; message?: unknown };
      const message = body.detail ?? body.message;
      if (typeof message === "string" && message.trim().length > 0) {
        errorMessage = message;
      }
    } catch {
      // Ignore JSON parse error, use default message
    }
    throw new AiSearchApiError(res.status, errorMessage);
  }

  return (await res.json()) as AiSearchResult;
}
