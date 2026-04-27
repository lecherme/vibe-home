"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { propertiesApi } from "@/lib/api/properties";
import type { PropertyListResponse } from "@/types/property";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";

function PropertyListContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const page = Number(searchParams.get("page")) || 1;
  const pageSize = 12;

  const [data, setData] = useState<PropertyListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    propertiesApi.list(page, pageSize)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch((err: any) => {
        if (isMounted) {
          setError(err.message || "Failed to load properties");
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [page]);

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(newPage));
    router.push(`/properties?${params.toString()}`);
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Properties</h1>
        <PropertyListSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 text-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 inline-block max-w-lg">
          <h3 className="text-red-800 font-bold mb-2">Error Loading Properties</h3>
          <p className="text-red-700 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-8 text-left">Properties</h1>
        <div className="bg-white border border-slate-200 rounded-lg py-16 px-4">
          <p className="text-slate-500 text-lg">No properties found.</p>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / data.page_size);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Properties</h1>
        <p className="text-slate-500">
          Showing {data.items.length} of {data.total} properties
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {data.items.map((property) => (
          <PropertyCard key={property.id} property={property} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 py-4">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
            className="px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
          >
            Previous
          </button>
          <span className="text-slate-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= totalPages}
            className="px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default function PropertiesPage() {
  return (
    <Suspense fallback={
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Properties</h1>
        <PropertyListSkeleton />
      </div>
    }>
      <PropertyListContent />
    </Suspense>
  );
}
