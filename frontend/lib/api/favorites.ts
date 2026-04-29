import { getAccessToken } from "@/lib/auth/session";
import type { FavoriteList } from "@/types/favorites";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function addFavorite(propertyId: string): Promise<void> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new Error("No active session");
  }

  const res = await fetch(`${apiUrl}/api/v1/favorites/${encodeURIComponent(propertyId)}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`);
  }
}

export async function removeFavorite(propertyId: string): Promise<void> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new Error("No active session");
  }

  const res = await fetch(`${apiUrl}/api/v1/favorites/${encodeURIComponent(propertyId)}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`);
  }
}

export async function getFavorites(
  page = 1,
  pageSize = 12,
): Promise<FavoriteList> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new Error("No active session");
  }

  const url = new URL("/api/v1/favorites", `${apiUrl.replace(/\/$/, "")}/`);
  url.searchParams.set("page", String(page));
  url.searchParams.set("page_size", String(pageSize));

  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`);
  }

  return res.json() as Promise<FavoriteList>;
}

export const favoritesApi = {
  addFavorite,
  removeFavorite,
  getFavorites,
};
