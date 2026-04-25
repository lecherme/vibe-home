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
