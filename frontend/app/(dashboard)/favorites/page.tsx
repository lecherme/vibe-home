"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { favoritesApi } from "@/lib/api/favorites";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";
import type { Property } from "@/types/property";

const PAGE_SIZE = 12;

function parsePage(value: string | null) {
  const page = Number(value);
  return Number.isFinite(page) && page > 0 ? page : 1;
}

function FavoritesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialPage = parsePage(searchParams.get("page"));
  const [favorites, setFavorites] = useState<Property[]>([]);
  const [page, setPage] = useState(initialPage);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const setPageAndUrl = useCallback((nextPage: number) => {
    setPage(nextPage);

    const params = new URLSearchParams(searchParams.toString());
    if (nextPage > 1) {
      params.set("page", String(nextPage));
    } else {
      params.delete("page");
    }

    const query = params.toString();
    router.push(query ? `/favorites?${query}` : "/favorites");
  }, [router, searchParams]);

  const loadFavorites = useCallback(async (currentPage: number) => {
    setIsLoading(true);
    const data = await favoritesApi.getFavorites(currentPage, PAGE_SIZE);
    setFavorites(data.items);
    setTotal(data.total);
    setError(null);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    const urlPage = parsePage(searchParams.get("page"));
    if (urlPage !== page) {
      setPage(urlPage);
    }
  }, [page, searchParams]);

  useEffect(() => {
    let isMounted = true;

    loadFavorites(page).catch((err: any) => {
      if (isMounted) {
        setError(err.message || "Failed to load favorites");
        setIsLoading(false);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [loadFavorites, page]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">My Favorites</h1>
        <PropertyListSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">My Favorites</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-12 flex flex-col items-center text-center">
          <div className="mb-4 text-red-400">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-red-800 font-bold text-xl mb-2">Failed to load favorites</h3>
          <p className="text-red-700 mb-6 max-w-md">{error}</p>
          <button 
            onClick={() => window.location.reload()}
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

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-8">My Favorites</h1>
      
      {favorites.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
          <div className="mb-4 text-slate-300">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              className="w-16 h-16 mx-auto"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-slate-700 mb-2">No favorites yet</h2>
          <p className="text-slate-500 max-w-md mx-auto mb-8">
            Start exploring properties and save the ones you love to see them here.
          </p>
          <a
            href="/properties"
            className="inline-flex items-center px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
          >
            Browse Properties
          </a>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {favorites.map((property) => (
              <PropertyCard
                key={property.id}
                property={property}
                isFavorited={true}
                onFavoriteToggle={(newState) => {
                  if (!newState) {
                    if (favorites.length > 1) {
                      loadFavorites(page).catch((err: any) => {
                        setError(err.message || "Failed to load favorites");
                        setIsLoading(false);
                      });
                    } else if (page > 1) {
                      setPageAndUrl(page - 1);
                    } else {
                      loadFavorites(page).catch((err: any) => {
                        setError(err.message || "Failed to load favorites");
                        setIsLoading(false);
                      });
                    }
                  }
                }}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => setPageAndUrl(page - 1)}
                disabled={page <= 1 || isLoading}
                className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-slate-700">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPageAndUrl(page + 1)}
                disabled={page >= totalPages || isLoading}
                className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function FavoritesPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">My Favorites</h1>
        <PropertyListSkeleton />
      </div>
    }>
      <FavoritesContent />
    </Suspense>
  );
}
