export type PropertyStatus = "available" | "sold" | "rented";

export interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  area_sqm: number;
  built_year: number | null;
  subway_distance_m: number | null;
  tags: string[];
  images: string[];
  status: PropertyStatus;
  created_at: string;
}

export interface PropertyListResponse {
  items: Property[];
  total: number;
  page: number;
  page_size: number;
}
