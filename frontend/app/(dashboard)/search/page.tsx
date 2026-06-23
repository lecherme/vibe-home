"use client";

import React, { useState, useEffect, useCallback, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { propertiesApi } from "@/lib/api/properties";
import { favoritesApi } from "@/lib/api/favorites";
import { aiSearch } from "@/lib/api/ai-search";
import type { AiSearchResult } from "@/types/ai-search";
import type { SearchFilters, SearchResult } from "@/types/search";
import type { PropertyStatus } from "@/types/property";
import { SearchBar } from "@/components/features/search/search-bar";
import { FilterPanel } from "@/components/features/search/filter-panel";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";
import { PaginationControls } from "@/components/features/common/PaginationControls";
import { AiSearchBar } from "@/components/features/search/ai-search-bar";
import { AiParsedFiltersCard } from "@/components/features/search/ai-parsed-filters-card";
import { AiSearchResults } from "@/components/features/search/ai-search-results";
import { InterpretedNeedsCard } from "@/components/features/search/interpreted-needs-card";

const PAGE_SIZE = 9;

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  // Mode state
  const [searchMode, setSearchMode] = useState<"filter" | "ai">("filter");

  // Shared state
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());

  // Local state for inputs to keep them snappy while typing
  const [location, setLocation] = useState(searchParams.get("location") || "");
  const [filters, setFilters] = useState<SearchFilters>({
    min_price: searchParams.get("min_price") ? Number(searchParams.get("min_price")) : undefined,
    max_price: searchParams.get("max_price") ? Number(searchParams.get("max_price")) : undefined,
    bedrooms_min: searchParams.get("bedrooms_min") ? Number(searchParams.get("bedrooms_min")) : undefined,
    bedrooms_max: searchParams.get("bedrooms_max") ? Number(searchParams.get("bedrooms_max")) : undefined,
    bathrooms_min: searchParams.get("bathrooms_min") ? Number(searchParams.get("bathrooms_min")) : undefined,
    bathrooms_max: searchParams.get("bathrooms_max") ? Number(searchParams.get("bathrooms_max")) : undefined,
    status: (searchParams.get("status") as PropertyStatus) || undefined,
  });

  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const searchIdRef = useRef(0);

  const page = Number(searchParams.get("page")) || 1;

  // AI Search State
  const [aiQuery, setAiQuery] = useState("");
  const [aiResult, setAiResult] = useState<AiSearchResult | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiPage, setAiPage] = useState(1);

  const performSearch = useCallback(async (
    loc: string,
    f: SearchFilters,
    p: number
  ) => {
    const currentId = ++searchIdRef.current;
    setLoading(true);
    setError(null);
    try {
      const searchFilters: SearchFilters = {
        ...f,
        location: loc || undefined,
      };

      const [searchData, favoritesRes] = await Promise.all([
        propertiesApi.searchProperties(searchFilters, p, PAGE_SIZE),
        favoritesApi.getAllFavoriteIds().catch(() => new Set<string>())
      ]);

      if (searchIdRef.current !== currentId) return;
      setResult(searchData);
      setFavoriteIds(favoritesRes);
    } catch (err: any) {
      if (searchIdRef.current !== currentId) return;
      setResult(null);
      setError(err.message || "Failed to fetch properties");
    } finally {
      if (searchIdRef.current === currentId) setLoading(false);
    }
  }, []);

  // Sync state and trigger search when URL parameters change
  useEffect(() => {
    if (searchMode === "ai") return; // Do not trigger standard search when in AI mode
    
    const loc = searchParams.get("location") || "";
    const f: SearchFilters = {
      min_price: searchParams.get("min_price") ? Number(searchParams.get("min_price")) : undefined,
      max_price: searchParams.get("max_price") ? Number(searchParams.get("max_price")) : undefined,
      bedrooms_min: searchParams.get("bedrooms_min") ? Number(searchParams.get("bedrooms_min")) : undefined,
      bedrooms_max: searchParams.get("bedrooms_max") ? Number(searchParams.get("bedrooms_max")) : undefined,
      bathrooms_min: searchParams.get("bathrooms_min") ? Number(searchParams.get("bathrooms_min")) : undefined,
      bathrooms_max: searchParams.get("bathrooms_max") ? Number(searchParams.get("bathrooms_max")) : undefined,
      status: (searchParams.get("status") as PropertyStatus) || undefined,
    };
    const p = Number(searchParams.get("page")) || 1;

    setLocation(loc);
    setFilters(f);
    performSearch(loc, f, p);
  }, [searchParams, performSearch, retryCount, searchMode]);

  const updateURL = (loc: string, f: SearchFilters, p: number) => {
    const params = new URLSearchParams();
    if (loc) params.set("location", loc);
    if (f.min_price) params.set("min_price", String(f.min_price));
    if (f.max_price) params.set("max_price", String(f.max_price));
    if (f.bedrooms_min) params.set("bedrooms_min", String(f.bedrooms_min));
    if (f.bedrooms_max) params.set("bedrooms_max", String(f.bedrooms_max));
    if (f.bathrooms_min) params.set("bathrooms_min", String(f.bathrooms_min));
    if (f.bathrooms_max) params.set("bathrooms_max", String(f.bathrooms_max));
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

  const performAiSearch = async (query: string, pageNum: number) => {
    setAiLoading(true);
    setAiError(null);
    try {
      const [data, favRes] = await Promise.all([
        aiSearch(query, pageNum, PAGE_SIZE),
        favoritesApi.getAllFavoriteIds().catch(() => new Set<string>())
      ]);
      setAiResult(data as AiSearchResult);
      setFavoriteIds(favRes);
    } catch (err: any) {
      setAiResult(null);
      setAiError(err.message || "Failed to fetch properties with AI");
    } finally {
      setAiLoading(false);
    }
  };

  const handleAiSearch = async (query: string) => {
    setAiQuery(query);
    setAiPage(1);
    await performAiSearch(query, 1);
  };

  const handleAiPageChange = async (newPage: number) => {
    setAiPage(newPage);
    await performAiSearch(aiQuery, newPage);
  };

  const totalPages = result ? Math.ceil(result.total / PAGE_SIZE) : 0;
  const aiTotalPages = aiResult ? Math.ceil(aiResult.total / PAGE_SIZE) : 0;
  const hasGroupedAiItems = aiResult != null && (aiResult.strict_items !== undefined || aiResult.recommended_items !== undefined);
  const hasAiItems = aiResult != null && (
    hasGroupedAiItems
      ? (aiResult.strict_items?.length ?? 0) > 0 || (aiResult.recommended_items?.length ?? 0) > 0
      : aiResult.items.length > 0
  );
  const hasActiveFilters = Boolean(location.trim()) ||
    filters.min_price !== undefined ||
    filters.max_price !== undefined ||
    filters.bedrooms_min !== undefined ||
    filters.bedrooms_max !== undefined ||
    filters.bathrooms_min !== undefined ||
    filters.bathrooms_max !== undefined ||
    Boolean(filters.status);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Search Properties</h1>
        
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setSearchMode("filter")}
            className={`py-2 px-4 border-b-2 font-medium text-sm transition-colors ${
              searchMode === "filter"
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Filter Search
          </button>
          <button
            onClick={() => setSearchMode("ai")}
            className={`py-2 px-4 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
              searchMode === "ai"
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            ✨ AI Search
          </button>
        </div>
        
        {searchMode === "filter" ? (
          <>
            <div className="flex flex-wrap items-center gap-2">
              <div className="flex-1 min-w-0">
                <SearchBar
                  value={location}
                  onChange={setLocation}
                  onSearch={handleSearch}
                  isLoading={loading}
                />
              </div>
              <button
                onClick={handleClearFilters}
                disabled={!hasActiveFilters || loading}
                className="inline-flex shrink-0 items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Clear Filters
              </button>
            </div>
            
            <FilterPanel 
              filters={filters} 
              onChange={(newFilters) => {
                setFilters(newFilters);
                updateURL(location, newFilters, 1);
              }}
              isLoading={loading}
            />
          </>
        ) : (
          <div className="mb-8">
            <AiSearchBar onSearch={handleAiSearch} isLoading={aiLoading} />
            {aiResult && (
              <>
                <AiParsedFiltersCard
                  queryParsed={aiResult.query_parsed}
                  parsedFilters={aiResult.parsed_filters}
                  aiSummary={aiResult.ai_summary}
                  parsedConstraints={aiResult.parsed_constraints}
                />
                <InterpretedNeedsCard
                  interpretedNeeds={aiResult.interpreted_needs}
                  interpretedIntent={aiResult.interpreted_intent}
                />
              </>
            )}
          </div>
        )}
      </div>

      {searchMode === "filter" && error && (
        <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-12 flex flex-col items-center text-center">
          <div className="mb-4 text-red-400">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-red-800 font-bold text-xl mb-2">Search failed</h3>
          <p className="text-red-700 mb-6 max-w-md">{error}</p>
          <button 
            onClick={() => setRetryCount(prev => prev + 1)}
            className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try Again
          </button>
        </div>
      )}

      {searchMode === "ai" && aiError && (
        <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-12 flex flex-col items-center text-center">
          <div className="mb-4 text-red-400">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-red-800 font-bold text-xl mb-2">AI Search failed</h3>
          <p className="text-red-700 mb-6 max-w-md">{aiError}</p>
          <button 
            onClick={() => performAiSearch(aiQuery, aiPage)}
            className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try Again
          </button>
        </div>
      )}

      {searchMode === "filter" ? (
        loading && !result ? (
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

            <PaginationControls
              page={page}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              isLoading={loading}
              className="mt-8"
            />
          </>
        ) : (
          !loading && !error && (
            <div className="text-center py-20 bg-white rounded-lg border border-dashed border-gray-300">
              <div className="mb-4 text-gray-300">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <p className="text-gray-600 text-lg font-medium">No properties found matching your criteria.</p>
              <p className="text-gray-400 text-sm mt-2 mb-6">Try adjusting your filters or search area.</p>
              <button
                onClick={handleClearFilters}
                className="inline-flex items-center px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
              >
                Clear all filters
              </button>
            </div>
          )
        )
      ) : (
        aiLoading && !aiResult ? (
          <PropertyListSkeleton />
        ) : hasAiItems && aiResult ? (
          <>
            <div className="mb-8">
              <AiSearchResults result={aiResult} favoriteIds={favoriteIds} />
            </div>

            <PaginationControls
              page={aiPage}
              totalPages={aiTotalPages}
              onPageChange={handleAiPageChange}
              isLoading={aiLoading}
              className="mt-8"
            />
          </>
        ) : (
          !aiLoading && !aiError && aiQuery && (
            <div className="text-center py-20 bg-white rounded-lg border border-dashed border-gray-300">
              <div className="mb-4 text-gray-300">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <p className="text-gray-600 text-lg font-medium">No properties found matching your AI query.</p>
              <p className="text-gray-400 text-sm mt-2 mb-6">Try rewording your prompt or making it broader.</p>
            </div>
          )
        )
      )}
      
      {((searchMode === "filter" && loading && result) || (searchMode === "ai" && aiLoading && aiResult)) && (
        <div className="pointer-events-none fixed inset-0 bg-white/50 flex items-center justify-center z-50">
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
