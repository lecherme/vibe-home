export interface AdminPropertyCreate {
  title: string;
  description: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  area: number;
  image_url: string;
}

export interface AdminPropertyUpdate extends Partial<AdminPropertyCreate> {}
