import React from "react";
import type { Property } from "@/types/property";

interface PropertyDetailProps {
  property: Property;
}

export function PropertyDetail({ property }: PropertyDetailProps) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="lg:grid lg:grid-cols-2 lg:items-start lg:gap-x-8">
        {/* Image gallery */}
        <div className="flex flex-col-reverse">
          <div className="aspect-h-3 aspect-w-4 overflow-hidden rounded-lg bg-gray-100">
            {property.images.length > 0 ? (
              <img
                src={property.images[0]}
                alt={property.title}
                className="h-full w-full object-cover object-center"
              />
            ) : (
              <div className="flex h-full items-center justify-center text-gray-400">
                No Image Available
              </div>
            )}
          </div>
          {property.images.length > 1 && (
            <div className="mt-6 grid grid-cols-4 gap-4">
              {property.images.slice(1, 5).map((image, idx) => (
                <div key={idx} className="aspect-h-1 aspect-w-1 relative overflow-hidden rounded-md bg-gray-100">
                  <img
                    src={image}
                    alt={`${property.title} ${idx + 2}`}
                    className="h-full w-full object-cover object-center"
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Property info */}
        <div className="mt-10 px-4 sm:mt-16 sm:px-0 lg:mt-0">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">{property.title}</h1>
              <p className="mt-2 text-lg text-gray-500">📍 {property.location}</p>
            </div>
            <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${
              property.status === 'available' ? 'bg-green-100 text-green-800' :
              property.status === 'sold' ? 'bg-red-100 text-red-800' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {property.status}
            </span>
          </div>

          <div className="mt-6">
            <h2 className="sr-only">Property information</h2>
            <p className="text-3xl font-bold text-gray-900">${property.price.toLocaleString()}</p>
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 border-y border-gray-200 py-6 sm:grid-cols-4">
            <div className="text-center">
              <p className="text-sm text-gray-500">Bedrooms</p>
              <p className="text-xl font-semibold text-gray-900">🛏️ {property.bedrooms}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Bathrooms</p>
              <p className="text-xl font-semibold text-gray-900">🚿 {property.bathrooms}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Area</p>
              <p className="text-xl font-semibold text-gray-900">📐 {property.area_sqm} m²</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Type</p>
              <p className="text-xl font-semibold text-gray-900">🏠 Property</p>
            </div>
          </div>

          <div className="mt-8">
            <h3 className="text-sm font-medium text-gray-900">Description</h3>
            <div className="mt-4 prose prose-sm text-gray-500 whitespace-pre-wrap">
              {property.description}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
