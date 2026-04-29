"use client";

import React, { useState, useEffect, useCallback } from "react";
import { propertiesApi } from "@/lib/api/properties";
import type { SearchFilters, SearchResult } from "@/types/search";
import { SearchBar } from "@/components/features/search/search-bar";
import { FilterPanel } from "@/components/features/search/filter-panel";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";

const PAGE_SIZE = 9;

export default function SearchPage() {
  const [location, setLocation] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({});
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const performSearch = useCallback(async (searchPage: number) => {
    setLoading(true);
    setError(null);
    try {
      const searchFilters: SearchFilters = {
        ...filters,
        location: location || undefined,
      };
      const data = await propertiesApi.searchProperties(searchFilters, searchPage, PAGE_SIZE);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch properties");
    } finally {
      setLoading(false);
    }
  }, [location, filters]);

  // Initial search
  useEffect(() => {
    performSearch(1);
  }, []);

  const handleSearch = () => {
    setPage(1);
    performSearch(1);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    performSearch(newPage);
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
          onChange={setFilters}
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
              <PropertyCard key={property.id} property={property} />
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
              onClick={() => {
                setLocation("");
                setFilters({});
                setPage(1);
                // We'll let the next effect trigger the search
              }}
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
