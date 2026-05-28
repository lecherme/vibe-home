import type { Property, PropertyStatus } from "@/types/property";

export interface SearchFilters {
  location?: string;
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
  bathrooms?: number;
  status?: PropertyStatus;
}

export interface SearchResult {
  items: Property[];
  total: number;
  page: number;
  page_size: number;
}
