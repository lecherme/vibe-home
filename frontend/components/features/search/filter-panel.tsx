"use client";

import React from "react";
import type { SearchFilters } from "@/types/search";
import type { PropertyStatus } from "@/types/property";

interface FilterPanelProps {
  filters: SearchFilters;
  onChange: (filters: SearchFilters) => void;
  isLoading?: boolean;
}

export function FilterPanel({ filters, onChange, isLoading }: FilterPanelProps) {
  const handleChange = (
    field: keyof SearchFilters,
    value: string | number | undefined
  ) => {
    onChange({
      ...filters,
      [field]: value === "" ? undefined : value,
    });
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
            value={filters.min_price ?? ""}
            onChange={(e) =>
              handleChange("min_price", e.target.value ? Number(e.target.value) : "")
            }
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
            value={filters.max_price ?? ""}
            onChange={(e) =>
              handleChange("max_price", e.target.value ? Number(e.target.value) : "")
            }
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
