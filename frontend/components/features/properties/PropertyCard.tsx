import Link from "next/link";
import type { Property } from "@/types/property";
import { cn } from "@/lib/utils";

interface PropertyCardProps {
  property: Property;
}

export function PropertyCard({ property }: PropertyCardProps) {
  const firstImage = property.images[0] || "/placeholder-property.jpg";

  return (
    <Link 
      href={`/properties/${property.id}`}
      className="group flex flex-col overflow-hidden rounded-lg border border-slate-200 bg-white transition-all hover:shadow-md"
    >
      <div className="relative aspect-[16/9] w-full overflow-hidden bg-slate-100">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={firstImage}
          alt={property.title}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute left-2 top-2">
          <span className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium uppercase tracking-wider",
            property.status === "available" ? "bg-green-100 text-green-700" :
            property.status === "sold" ? "bg-red-100 text-red-700" :
            "bg-blue-100 text-blue-700"
          )}>
            {property.status}
          </span>
        </div>
      </div>
      
      <div className="flex flex-1 flex-col p-4">
        <div className="mb-2">
          <h3 className="line-clamp-1 text-lg font-semibold text-slate-900">
            {property.title}
          </h3>
          <p className="line-clamp-1 text-sm text-slate-500">
            {property.location}
          </p>
        </div>

        <div className="mt-auto">
          <p className="text-xl font-bold text-slate-900">
            ${property.price.toLocaleString()}
          </p>
          
          <div className="mt-3 flex items-center gap-3 border-t border-slate-100 pt-3 text-sm text-slate-600">
            <div className="flex items-center gap-1">
              <span className="font-medium">{property.bedrooms}</span>
              <span>bed</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="font-medium">{property.bathrooms}</span>
              <span>bath</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="font-medium">{property.area_sqm}</span>
              <span>m²</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
