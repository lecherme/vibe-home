import { getAccessToken } from "@/lib/auth/session";
import type { FavoriteList, FavoriteStatus } from "@/types/favorites";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class FavoriteConflictError extends Error {
  constructor(message = "Favorite already exists") {
    super(message);
    this.name = "FavoriteConflictError";
  }
}

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
    if (res.status === 409) {
      throw new FavoriteConflictError();
    }

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

export async function isFavorite(propertyId: string): Promise<boolean> {
  const accessToken = await getAccessToken();

  if (!accessToken) {
    throw new Error("No active session");
  }

  const res = await fetch(`${apiUrl}/api/v1/favorites/${encodeURIComponent(propertyId)}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`);
  }

  const data = await (res.json() as Promise<FavoriteStatus>);
  return data.is_favorite;
}

export const favoritesApi = {
  addFavorite,
  removeFavorite,
  getFavorites,
  isFavorite,
};
