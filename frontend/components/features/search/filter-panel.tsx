"use client";

import React, { useEffect, useRef, useState } from "react";
import type { SearchFilters } from "@/types/search";
import type { PropertyStatus } from "@/types/property";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div>
          <Label
            htmlFor="min_price"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Min Price
          </Label>
          <Input
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
          <Label
            htmlFor="max_price"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Max Price
          </Label>
          <Input
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
          <Label
            htmlFor="bedrooms"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Min Bedrooms
          </Label>
          <Select
            value={filters.bedrooms?.toString() ?? "any"}
            onValueChange={(val) =>
              handleChange("bedrooms", val === "any" ? undefined : Number(val))
            }
          >
            <SelectTrigger id="bedrooms" disabled={isLoading} className="w-full">
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Any</SelectItem>
              {[1, 2, 3, 4, 5].map((num) => (
                <SelectItem key={num} value={String(num)}>
                  {num}+ beds
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label
            htmlFor="status"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Status
          </Label>
          <Select
            value={filters.status ?? "any"}
            onValueChange={(val) =>
              handleChange("status", val === "any" ? undefined : (val as PropertyStatus))
            }
          >
            <SelectTrigger id="status" disabled={isLoading} className="w-full">
              <SelectValue placeholder="Any Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Any Status</SelectItem>
              <SelectItem value="available">Available</SelectItem>
              <SelectItem value="sold">Sold</SelectItem>
              <SelectItem value="rented">Rented</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label
            htmlFor="bathrooms"
            className="block text-xs font-medium text-gray-700 mb-1"
          >
            Min Bathrooms
          </Label>
          <Select
            value={filters.bathrooms?.toString() ?? "any"}
            onValueChange={(val) =>
              handleChange("bathrooms", val === "any" ? undefined : Number(val))
            }
          >
            <SelectTrigger id="bathrooms" disabled={isLoading} className="w-full">
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Any</SelectItem>
              {[1, 2, 3, 4, 5].map((num) => (
                <SelectItem key={num} value={String(num)}>
                  {num}+ baths
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
