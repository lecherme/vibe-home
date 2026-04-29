"use client";

import { useEffect, useState } from "react";
import { favoritesApi } from "@/lib/api/favorites";
import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { PropertyListSkeleton } from "@/components/features/properties/PropertyListSkeleton";
import type { Property } from "@/types/property";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    
    async function loadFavorites() {
      try {
        setIsLoading(true);
        const data = await favoritesApi.getFavorites();
        if (isMounted) {
          setFavorites(data.items);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || "Failed to load favorites");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadFavorites();

    return () => {
      isMounted = false;
    };
  }, []);

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
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 font-medium mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
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
        <div className="text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
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
            className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Browse Properties
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {favorites.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>
      )}
    </div>
  );
}
