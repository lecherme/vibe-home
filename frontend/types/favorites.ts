import type { Property as PropertyRead } from "@/types/property";

export interface Favorite {
  propertyId: string;
  userId: string;
  createdAt: string;
}

export interface FavoriteList {
  items: PropertyRead[];
  total: number;
}

export interface FavoriteStatus {
  is_favorite: boolean;
}
