"use client";

import React, { useState, useRef, useEffect } from "react";
import { favoritesApi, FavoriteConflictError } from "@/lib/api/favorites";

interface FavoriteButtonProps {
  propertyId: string;
  initialIsFavorited?: boolean;
  onToggle?: (isFavorited: boolean) => void;
}

export function FavoriteButton({
  propertyId,
  initialIsFavorited = false,
  onToggle,
}: FavoriteButtonProps) {
  const [isFavorited, setIsFavorited] = useState(initialIsFavorited);
  const [isLoading, setIsLoading] = useState(false);
  const hasInteracted = useRef(false);

  useEffect(() => {
    if (!hasInteracted.current) {
      setIsFavorited(initialIsFavorited ?? false);
    }
  }, [initialIsFavorited]);

  const toggleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (isLoading) return;

    hasInteracted.current = true;
    const previousState = isFavorited;
    
    // Optimistic update
    setIsFavorited(!previousState);
    setIsLoading(true);

    try {
      if (previousState) {
        await favoritesApi.removeFavorite(propertyId);
      } else {
        await favoritesApi.addFavorite(propertyId);
      }
      onToggle?.(!previousState);
    } catch (error) {
      if (error instanceof FavoriteConflictError) {
        // If it's already favorited, just keep it favorited and don't show error
        setIsFavorited(true);
        onToggle?.(true);
      } else {
        // Revert state on other errors
        console.error("Failed to update favorite status:", error);
        setIsFavorited(previousState);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={toggleFavorite}
      disabled={isLoading}
      className={`p-2 rounded-full transition-colors flex items-center justify-center ${
        isFavorited
          ? "text-red-500 bg-red-50"
          : "text-slate-400 bg-slate-100 hover:text-red-500 hover:bg-red-50"
      }`}
      aria-label={isFavorited ? "Remove from favorites" : "Add to favorites"}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill={isFavorited ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-5 h-5"
      >
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l8.84-8.84 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
    </button>
  );
}
