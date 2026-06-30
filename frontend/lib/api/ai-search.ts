import { apiUrl } from "@/lib/api/config";
import { getAccessToken } from "@/lib/auth/session";
import type {
  AiSearchErrorEventData,
  AiSearchParsedEventData,
  AiSearchResult,
  AiSearchResultsEventData,
  AiSearchSearchingEventData,
  AiSearchStreamEmpty,
  AiSearchSummaryEventData,
} from "@/types/ai-search";
import type { AiSearchRequest } from "@/types/search";

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

async function getAuthHeaders(contentType?: string): Promise<HeadersInit> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new AiSearchApiError(401, "No active session");
  }

  const headers: Record<string, string> = {
    Authorization: `Bearer ${accessToken}`,
  };

  if (contentType) {
    headers["Content-Type"] = contentType;
  }

  return headers;
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
    headers: await getAuthHeaders("application/json"),
    body: JSON.stringify(reqBody),
  });

  if (!res.ok) {
    throw new AiSearchApiError(res.status, await getErrorMessage(res));
  }

  return res.json() as Promise<AiSearchResult>;
}

export interface AiSearchStreamCallbacks {
  onStarted?: (data: AiSearchStreamEmpty) => void;
  onParsed?: (data: AiSearchParsedEventData) => void;
  onSearching?: (data: AiSearchSearchingEventData) => void;
  onResults?: (data: AiSearchResultsEventData) => void;
  onSummary?: (data: AiSearchSummaryEventData) => void;
  onDone?: (data: AiSearchStreamEmpty) => void;
  onError?: (data: AiSearchErrorEventData) => void;
}

function parseSseEventBlock(block: string): { event: string; data: string } | null {
  let eventName = "";
  const dataLines: string[] = [];

  for (const line of block.split("\n")) {
    if (!line || line.startsWith(":")) {
      continue;
    }

    if (line.startsWith("event:")) {
      eventName = line.slice("event:".length).trim();
      continue;
    }

    if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trimStart());
    }
  }

  if (!eventName) {
    return null;
  }

  return {
    event: eventName,
    data: dataLines.join("\n") || "{}",
  };
}

function dispatchStreamEvent(
  event: string,
  data: string,
  callbacks: AiSearchStreamCallbacks
): void {
  switch (event) {
    case "started":
      callbacks.onStarted?.(JSON.parse(data) as AiSearchStreamEmpty);
      return;
    case "parsed":
      callbacks.onParsed?.(JSON.parse(data) as AiSearchParsedEventData);
      return;
    case "searching":
      callbacks.onSearching?.(JSON.parse(data) as AiSearchSearchingEventData);
      return;
    case "results":
      callbacks.onResults?.(JSON.parse(data) as AiSearchResultsEventData);
      return;
    case "summary":
      callbacks.onSummary?.(JSON.parse(data) as AiSearchSummaryEventData);
      return;
    case "done":
      callbacks.onDone?.(JSON.parse(data) as AiSearchStreamEmpty);
      return;
    case "error":
      callbacks.onError?.(JSON.parse(data) as AiSearchErrorEventData);
      return;
    default:
      return;
  }
}

export function aiSearchStream(
  query: string,
  page = 1,
  pageSize = 20,
  callbacks: AiSearchStreamCallbacks = {}
): AbortController {
  const abortController = new AbortController();

  void (async () => {
    try {
      const url = new URL("/api/v1/search/ai/stream", `${apiUrl.replace(/\/$/, "")}/`);
      url.searchParams.set("query", query);
      url.searchParams.set("page", String(page));
      url.searchParams.set("page_size", String(pageSize));

      const res = await fetch(url, {
        method: "GET",
        headers: {
          ...(await getAuthHeaders()),
          Accept: "text/event-stream",
        },
        signal: abortController.signal,
      });

      if (!res.ok) {
        callbacks.onError?.({
          message: await getErrorMessage(res),
        });
        return;
      }

      if (!res.body) {
        callbacks.onError?.({
          message: "Empty AI search stream response",
        });
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        buffer = buffer.replace(/\r/g, "");

        let boundaryIndex = buffer.indexOf("\n\n");
        while (boundaryIndex !== -1) {
          const block = buffer.slice(0, boundaryIndex).trim();
          buffer = buffer.slice(boundaryIndex + 2);

          if (block) {
            const parsedEvent = parseSseEventBlock(block);
            if (parsedEvent) {
              dispatchStreamEvent(parsedEvent.event, parsedEvent.data, callbacks);
            }
          }

          boundaryIndex = buffer.indexOf("\n\n");
        }
      }

      const remainingBlock = buffer.replace(/\r/g, "").trim();
      if (remainingBlock) {
        const parsedEvent = parseSseEventBlock(remainingBlock);
        if (parsedEvent) {
          dispatchStreamEvent(parsedEvent.event, parsedEvent.data, callbacks);
        }
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        return;
      }

      if (error instanceof AiSearchApiError) {
        callbacks.onError?.({ message: error.message });
        return;
      }

      callbacks.onError?.({
        message: error instanceof Error ? error.message : "AI search stream failed",
      });
    }
  })();

  return abortController;
}
