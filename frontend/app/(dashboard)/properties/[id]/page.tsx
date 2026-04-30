"use client";

import { useEffect, useState } from "react";
import { useParams, notFound } from "next/navigation";
import { propertiesApi, PropertyApiError } from "@/lib/api/properties";
import { favoritesApi } from "@/lib/api/favorites";
import type { Property } from "@/types/property";
import { PropertyDetail } from "@/components/features/properties/PropertyDetail";
import { FavoriteButton } from "@/components/features/favorites/favorite-button";

export default function PropertyDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [property, setProperty] = useState<Property | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFavorited, setIsFavorited] = useState(false);

  useEffect(() => {
    if (!id) return;

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    propertiesApi.get(id)
      .then((res) => {
        if (isMounted) {
          setProperty(res);
          setIsLoading(false);
        }
      })
      .catch((err: any) => {
        if (isMounted) {
          if (err instanceof PropertyApiError && err.status === 404) {
            setError("404");
          } else {
            setError(err.message || "Failed to load property details");
          }
          setIsLoading(false);
        }
      });

    favoritesApi.getFavorites()
      .then((data) => {
        if (isMounted) {
          setIsFavorited(data.items.some((p) => p.id === id));
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, [id]);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8 text-center">
        <div className="animate-pulse space-y-8">
          <div className="aspect-[16/10] bg-slate-200 rounded-xl" />
          <div className="space-y-4">
            <div className="h-8 bg-slate-200 rounded w-1/3 mx-auto" />
            <div className="h-4 bg-slate-200 rounded w-1/4 mx-auto" />
          </div>
        </div>
      </div>
    );
  }

  if (error === "404") {
    notFound();
    return null;
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8 text-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 inline-block">
          <h3 className="text-red-800 font-bold mb-2">Error Loading Property</h3>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  if (!property) {
    notFound();
    return null;
  }

  return (
    <div className="relative max-w-5xl mx-auto">
      <div className="absolute top-12 right-8 z-10 md:top-14 md:right-12">
        <FavoriteButton propertyId={property.id} initialIsFavorited={isFavorited} />
      </div>
      <PropertyDetail property={property} />
    </div>
  );
}
