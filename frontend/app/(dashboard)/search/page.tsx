"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { propertiesApi } from "@/lib/api/properties";
import { favoritesApi } from "@/lib/api/favorites";
import type { SearchFilters, SearchResult } from "@/types/search";
import type { PropertyStatus } from "@/types/property";
import { SearchBar } from "@/components/features/search/search-bar";
import { FilterPanel } from "@/components/features/search/filter-panel";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";

const PAGE_SIZE = 9;

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  // Local state for inputs to keep them snappy while typing
  const [location, setLocation] = useState(searchParams.get("location") || "");
  const [filters, setFilters] = useState<SearchFilters>({
    min_price: searchParams.get("min_price") ? Number(searchParams.get("min_price")) : undefined,
    max_price: searchParams.get("max_price") ? Number(searchParams.get("max_price")) : undefined,
    bedrooms: searchParams.get("bedrooms") ? Number(searchParams.get("bedrooms")) : undefined,
    status: (searchParams.get("status") as PropertyStatus) || undefined,
  });

  const [result, setResult] = useState<SearchResult | null>(null);
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const page = Number(searchParams.get("page")) || 1;

  const performSearch = useCallback(async (
    loc: string,
    f: SearchFilters,
    p: number
  ) => {
    setLoading(true);
    setError(null);
    try {
      const searchFilters: SearchFilters = {
        ...f,
        location: loc || undefined,
      };
      
      const [searchData, favoritesRes] = await Promise.all([
        propertiesApi.searchProperties(searchFilters, p, PAGE_SIZE),
        favoritesApi.getFavorites(1, 100).catch(() => ({ items: [], total: 0, page: 1, page_size: 100 }))
      ]);

      setResult(searchData);
      setFavoriteIds(new Set(favoritesRes.items.map(f => f.id)));
    } catch (err: any) {
      setError(err.message || "Failed to fetch properties");
    } finally {
      setLoading(false);
    }
  }, []);

  // Sync state and trigger search when URL parameters change
  useEffect(() => {
    const loc = searchParams.get("location") || "";
    const f: SearchFilters = {
      min_price: searchParams.get("min_price") ? Number(searchParams.get("min_price")) : undefined,
      max_price: searchParams.get("max_price") ? Number(searchParams.get("max_price")) : undefined,
      bedrooms: searchParams.get("bedrooms") ? Number(searchParams.get("bedrooms")) : undefined,
      status: (searchParams.get("status") as PropertyStatus) || undefined,
    };
    const p = Number(searchParams.get("page")) || 1;

    setLocation(loc);
    setFilters(f);
    performSearch(loc, f, p);
  }, [searchParams, performSearch]);

  const updateURL = (loc: string, f: SearchFilters, p: number) => {
    const params = new URLSearchParams();
    if (loc) params.set("location", loc);
    if (f.min_price) params.set("min_price", String(f.min_price));
    if (f.max_price) params.set("max_price", String(f.max_price));
    if (f.bedrooms) params.set("bedrooms", String(f.bedrooms));
    if (f.status) params.set("status", f.status);
    if (p > 1) params.set("page", String(p));
    
    router.push(`/search?${params.toString()}`);
  };

  const handleSearch = () => {
    updateURL(location, filters, 1);
  };

  const handlePageChange = (newPage: number) => {
    updateURL(location, filters, newPage);
  };

  const handleClearFilters = () => {
    setLocation("");
    setFilters({});
    updateURL("", {}, 1);
  };

  const totalPages = result ? Math.ceil(result.total / PAGE_SIZE) : 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Search Properties</h1>
        
        <SearchBar 
          value={location} 
          onChange={setLocation} 
          onSearch={handleSearch}
          isLoading={loading}
        />
        
        <FilterPanel 
          filters={filters} 
          onChange={(newFilters) => {
            setFilters(newFilters);
            updateURL(location, newFilters, 1);
          }}
          isLoading={loading}
        />
      </div>

      {error && (
        <div className="mb-8 rounded-md bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading && !result ? (
        <PropertyListSkeleton />
      ) : result && result.items.length > 0 ? (
        <>
          <div className="mb-4 text-sm text-gray-600">
            Found {result.total} properties
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {result.items.map((property) => (
              <PropertyCard 
                key={property.id} 
                property={property} 
                isFavorited={favoriteIds.has(property.id)}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1 || loading}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-700">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages || loading}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        !loading && (
          <div className="text-center py-12 bg-white rounded-lg border border-dashed border-gray-300">
            <p className="text-gray-500">No properties found matching your criteria.</p>
            <button
              onClick={handleClearFilters}
              className="mt-4 text-indigo-600 hover:text-indigo-500 font-medium"
            >
              Clear all filters
            </button>
          </div>
        )
      )}
      
      {loading && result && (
        <div className="fixed inset-0 bg-white/50 flex items-center justify-center z-50">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Search Properties</h1>
        <PropertyListSkeleton />
      </div>
    }>
      <SearchContent />
    </Suspense>
  );
}
