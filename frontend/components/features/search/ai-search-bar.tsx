"use client";

import React, { useState } from "react";
import { Input } from "@/components/ui/input";

interface AiSearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function AiSearchBar({ onSearch, isLoading = false }: AiSearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="flex w-full gap-2">
      <div className="relative flex-1">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <svg
            className="h-5 w-5 text-gray-400"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Describe the property you are looking for (e.g. A 2 bedroom apartment in Paris under $500k)..."
          className="block w-full rounded-md border-gray-300 py-2 pl-10 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>
      <button
        onClick={handleSearch}
        disabled={isLoading || !query.trim()}
        className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium shrink-0 bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {isLoading ? "Searching..." : "✨ AI Search"}
      </button>
    </div>
  );
}
