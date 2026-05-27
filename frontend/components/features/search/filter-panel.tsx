"use client";

import React, { useEffect, useRef, useState } from "react";
import type { SearchFilters } from "@/types/search";
import type { PropertyStatus } from "@/types/property";

interface FilterPanelProps {
  filters: SearchFilters;
  onChange: (filters: SearchFilters) => void;
  isLoading?: boolean;
}

export function FilterPanel({ filters, onChange, isLoading }: FilterPanelProps) {
  const [localMinPrice, setLocalMinPrice] = useState(
    filters.min_price?.toString() ?? ""
  );
  const [localMaxPrice, setLocalMaxPrice] = useState(
    filters.max_price?.toString() ?? ""
  );
  const priceDebounceTimers = useRef<
    Partial<Record<"min_price" | "max_price", ReturnType<typeof setTimeout>>>
  >({});
  const filtersRef = useRef(filters);

  useEffect(() => {
    filtersRef.current = filters;
    if (!priceDebounceTimers.current.min_price) {
      setLocalMinPrice(filters.min_price?.toString() ?? "");
    }
    if (!priceDebounceTimers.current.max_price) {
      setLocalMaxPrice(filters.max_price?.toString() ?? "");
    }
  }, [filters]);

  useEffect(() => {
    return () => {
      Object.values(priceDebounceTimers.current).forEach((timer) => {
        clearTimeout(timer);
      });
    };
  }, []);

  const handleChange = (
    field: keyof SearchFilters,
    value: string | number | undefined
  ) => {
    onChange({
      ...filtersRef.current,
      [field]: value === "" ? undefined : value,
    });
  };

  const handlePriceChange = (
    field: "min_price" | "max_price",
    value: string
  ) => {
    if (field === "min_price") {
      setLocalMinPrice(value);
    } else {
      setLocalMaxPrice(value);
    }

    const existingTimer = priceDebounceTimers.current[field];
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    priceDebounceTimers.current[field] = setTimeout(() => {
      handleChange(field, value ? Number(value) : "");
      delete priceDebounceTimers.current[field];
    }, 500);
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900 uppercase tracking-wider">
        Filters
      </h3>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label
            htmlFor="min_price"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Min Price
          </label>
          <input
            type="number"
            id="min_price"
            value={localMinPrice}
            onChange={(e) => handlePriceChange("min_price", e.target.value)}
            placeholder="No min"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            disabled={isLoading}
          />
        </div>

        <div>
          <label
            htmlFor="max_price"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Max Price
          </label>
          <input
            type="number"
            id="max_price"
            value={localMaxPrice}
            onChange={(e) => handlePriceChange("max_price", e.target.value)}
            placeholder="No max"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            disabled={isLoading}
          />
        </div>

        <div>
          <label
            htmlFor="bedrooms"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Min Bedrooms
          </label>
          <select
            id="bedrooms"
            value={filters.bedrooms ?? ""}
            onChange={(e) =>
              handleChange("bedrooms", e.target.value ? Number(e.target.value) : "")
            }
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            disabled={isLoading}
          >
            <option value="">Any</option>
            {[1, 2, 3, 4, 5].map((num) => (
              <option key={num} value={num}>
                {num}+ beds
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="status"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Status
          </label>
          <select
            id="status"
            value={filters.status ?? ""}
            onChange={(e) =>
              handleChange("status", e.target.value as PropertyStatus | "")
            }
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            disabled={isLoading}
          >
            <option value="">Any Status</option>
            <option value="available">Available</option>
            <option value="sold">Sold</option>
            <option value="rented">Rented</option>
          </select>
        </div>
      </div>
    </div>
  );
}
