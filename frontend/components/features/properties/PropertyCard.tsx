import React from "react";
import Link from "next/link";
import type { Property } from "@/types/property";

interface PropertyCardProps {
  property: Property;
}

export function PropertyCard({ property }: PropertyCardProps) {
  const firstImage = property.images[0] || "https://via.placeholder.com/400x300?text=No+Image";

  return (
    <Link
      href={`/properties/${property.id}`}
      className="group flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md"
    >
      <div className="relative aspect-video w-full overflow-hidden bg-gray-100">
        <img
          src={firstImage}
          alt={property.title}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute right-2 top-2">
          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            property.status === 'available' ? 'bg-green-100 text-green-800' :
            property.status === 'sold' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {property.status}
          </span>
        </div>
      </div>
      <div className="flex flex-1 flex-col p-4">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-lg font-bold text-gray-900">
            ${property.price.toLocaleString()}
          </p>
          <div className="flex gap-3 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <span>🛏️</span> {property.bedrooms}
            </span>
            <span className="flex items-center gap-1">
              <span>🚿</span> {property.bathrooms}
            </span>
          </div>
        </div>
        <h3 className="mb-1 text-base font-semibold text-gray-900 group-hover:text-blue-600">
          {property.title}
        </h3>
        <p className="text-sm text-gray-500 line-clamp-1">
          📍 {property.location}
        </p>
      </div>
    </Link>
  );
}
