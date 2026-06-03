export interface AdminPropertyCreate {
  title: string;
  description: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  area: number;
  images: string[];
}

export interface AdminPropertyUpdate extends Partial<AdminPropertyCreate> {}

export interface PropertyImageUploadResponse {
  url: string;
}
