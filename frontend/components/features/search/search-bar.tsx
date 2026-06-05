"use client";

import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  isLoading?: boolean;
}

export function SearchBar({ value, onChange, onSearch, isLoading }: SearchBarProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      onSearch();
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
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search by location (e.g. London, Tokyo)..."
          className="block w-full rounded-md border-gray-300 py-2 pl-10 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>
      <Button
        onClick={onSearch}
        disabled={isLoading}
        className="bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 w-28 shrink-0"
      >
        {isLoading ? "Searching..." : "Search"}
      </Button>
    </div>
  );
}
