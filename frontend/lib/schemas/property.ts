import { z } from "zod"

export const propertySchema = z.object({
  title: z.string().trim().min(1, "Title is required"),
  description: z.string().trim().min(1, "Description is required"),
  price: z.number().positive("Price must be positive"),
  location: z.string().trim().min(1, "Location is required"),
  bedrooms: z.number().int().min(1, "At least 1 bedroom required"),
  bathrooms: z.number().int().min(1, "At least 1 bathroom required"),
  area: z.number().positive("Area must be positive"),
  images: z.array(z.string()).min(1).max(5),
})

export type PropertyFormValues = z.infer<typeof propertySchema>
