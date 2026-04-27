import type { Property } from "@/types/property";
import { cn } from "@/lib/utils";

interface PropertyDetailProps {
  property: Property;
}

export function PropertyDetail({ property }: PropertyDetailProps) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        {/* Image Gallery */}
        <div className="grid grid-cols-1 gap-1 md:grid-cols-2">
          <div className="aspect-video w-full overflow-hidden bg-slate-100 md:aspect-auto">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={property.images[0] || "/placeholder-property.jpg"}
              alt={property.title}
              className="h-full w-full object-cover"
            />
          </div>
          <div className="hidden grid-cols-2 gap-1 md:grid">
            {property.images.slice(1, 5).map((image, i) => (
              <div key={i} className="aspect-square w-full overflow-hidden bg-slate-100">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={image}
                  alt={`${property.title} - ${i + 2}`}
                  className="h-full w-full object-cover"
                />
              </div>
            ))}
            {property.images.length < 5 && Array.from({ length: Math.max(0, 4 - property.images.length + 1) }).map((_, i) => (
              <div key={`placeholder-${i}`} className="aspect-square w-full bg-slate-50 flex items-center justify-center text-slate-300">
                No image
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 md:p-8">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <span className={cn(
                  "rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider",
                  property.status === "available" ? "bg-green-100 text-green-700" :
                  property.status === "sold" ? "bg-red-100 text-red-700" :
                  "bg-blue-100 text-blue-700"
                )}>
                  {property.status}
                </span>
                <span className="text-sm text-slate-500">
                  Added on {new Date(property.created_at).toLocaleDateString()}
                </span>
              </div>
              <h1 className="text-3xl font-bold text-slate-900 md:text-4xl">
                {property.title}
              </h1>
              <p className="mt-2 text-lg text-slate-600">
                {property.location}
              </p>
            </div>
            <div className="text-left md:text-right">
              <p className="text-sm font-medium text-slate-500 uppercase tracking-wide">Price</p>
              <p className="text-4xl font-extrabold text-slate-900">
                ${property.price.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 border-y border-slate-100 py-6 sm:grid-cols-4">
            <div className="flex flex-col items-center justify-center rounded-lg bg-slate-50 p-4">
              <span className="text-2xl font-bold text-slate-900">{property.bedrooms}</span>
              <span className="text-sm text-slate-500">Bedrooms</span>
            </div>
            <div className="flex flex-col items-center justify-center rounded-lg bg-slate-50 p-4">
              <span className="text-2xl font-bold text-slate-900">{property.bathrooms}</span>
              <span className="text-sm text-slate-500">Bathrooms</span>
            </div>
            <div className="flex flex-col items-center justify-center rounded-lg bg-slate-50 p-4">
              <span className="text-2xl font-bold text-slate-900">{property.area_sqm}</span>
              <span className="text-sm text-slate-500">Area (m²)</span>
            </div>
            <div className="flex flex-col items-center justify-center rounded-lg bg-slate-50 p-4">
              <span className="text-2xl font-bold text-slate-900 capitalize">{property.status}</span>
              <span className="text-sm text-slate-500">Status</span>
            </div>
          </div>

          <div className="mt-8">
            <h2 className="text-2xl font-bold text-slate-900">Description</h2>
            <div className="mt-4 prose prose-slate max-w-none text-slate-600 whitespace-pre-line">
              {property.description}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
