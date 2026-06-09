import type { Property, PropertyStatus } from "@/types/property";

export interface SearchFilters {
  location?: string;
  min_price?: number;
  max_price?: number;
  bedrooms_min?: number;
  bedrooms_max?: number;
  bathrooms_min?: number;
  bathrooms_max?: number;
  status?: PropertyStatus;
}

export interface SearchResult {
  items: Property[];
  total: number;
  page: number;
  page_size: number;
}

export interface AiSearchRequest {
  query: string;
  page?: number;
  page_size?: number;
}

export interface AiSearchResult extends SearchResult {
  parsed_filters: SearchFilters;
  ai_summary: string;
  query_parsed: boolean;
}
