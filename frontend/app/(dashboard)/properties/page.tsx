"use client";

import { useEffect, useState, Suspense, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { propertiesApi } from "@/lib/api/properties";
import { favoritesApi } from "@/lib/api/favorites";
import type { PropertyListResponse } from "@/types/property";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";
import { PaginationControls } from "@/components/features/common/PaginationControls";

function PropertyListContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const page = Number(searchParams.get("page")) || 1;
  const pageSize = 12;

  const [data, setData] = useState<PropertyListResponse | null>(null);
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  const fetchProperties = useCallback(() => {
    setIsLoading(true);
    setError(null);

    Promise.all([
      propertiesApi.list(page, pageSize),
      favoritesApi.getFavorites(1, 100).catch(() => ({ items: [], total: 0, page: 1, page_size: 100 }))
    ])
      .then(([propertiesRes, favoritesRes]) => {
        setData(propertiesRes);
        setFavoriteIds(new Set(favoritesRes.items.map(f => f.id)));
        setIsLoading(false);
      })
      .catch((err: any) => {
        setError(err.message || "Failed to load properties");
        setIsLoading(false);
      });
  }, [page, pageSize]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties, retryCount]);

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(newPage));
    router.push(`/properties?${params.toString()}`);
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
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
        <h1 className="text-3xl font-bold text-slate-900 mb-8 text-left">Properties</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-12 flex flex-col items-center">
          <div className="mb-4 text-red-400">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-red-800 font-bold text-xl mb-2">Oops! Something went wrong</h3>
          <p className="text-red-700 mb-6 max-w-md">{error}</p>
          <button 
            onClick={handleRetry}
            className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
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
        <div className="bg-white border border-slate-200 rounded-lg py-20 px-4">
          <div className="mb-4 text-slate-300">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <p className="text-slate-500 text-lg">No properties found.</p>
          <p className="text-slate-400 text-sm mt-2">Check back later or try adjusting your search.</p>
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
          <PropertyCard 
            key={property.id} 
            property={property} 
            isFavorited={favoriteIds.has(property.id)}
          />
        ))}
      </div>

      <PaginationControls
        page={page}
        totalPages={totalPages}
        onPageChange={handlePageChange}
        isLoading={isLoading}
        className="py-4"
      />
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
