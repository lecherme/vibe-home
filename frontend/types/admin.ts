export interface AdminPropertyCreate {
  title: string;
  description: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  area: number;
  images: string[];
  built_year?: number | null;
  subway_distance_m?: number | null;
  tags?: string[];
}

export interface AdminPropertyUpdate extends Partial<AdminPropertyCreate> {}

export interface PropertyImageUploadResponse {
  url: string;
}
