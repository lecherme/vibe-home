import React from "react";
import { notFound } from "next/navigation";
import { propertiesApi, PropertyApiError } from "@/lib/api/properties";
import { PropertyDetail } from "@/components/features/properties/PropertyDetail";

interface PropertyDetailPageProps {
  params: {
    id: string;
  };
}

export default async function PropertyDetailPage({
  params,
}: PropertyDetailPageProps) {
  const { id } = params;

  try {
    const property = await propertiesApi.get(id);
    return <PropertyDetail property={property} />;
  } catch (error) {
    if (error instanceof PropertyApiError && error.status === 404) {
      notFound();
    }
    
    console.error(`Failed to fetch property ${id}:`, error);
    
    return (
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 text-center">
        <h2 className="text-2xl font-bold text-red-600">Error loading property details</h2>
        <p className="mt-2 text-gray-600">
          We encountered a problem while fetching the property details. Please try again later.
        </p>
      </div>
    );
  }
}
