import React from "react";
import type { SearchFilters } from "@/types/search";

interface AiParsedFiltersCardProps {
  queryParsed: boolean;
  parsedFilters: SearchFilters;
  aiSummary: string;
}

export function AiParsedFiltersCard({
  queryParsed,
  parsedFilters,
  aiSummary,
}: AiParsedFiltersCardProps) {
  const renderChips = () => {
    const chips: React.ReactNode[] = [];

    if (parsedFilters.location) {
      chips.push(
        <span key="location" className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
          📍 {parsedFilters.location}
        </span>
      );
    }
    
    if (parsedFilters.min_price !== undefined || parsedFilters.max_price !== undefined) {
      let priceStr = "";
      if (parsedFilters.min_price !== undefined && parsedFilters.max_price !== undefined) {
        priceStr = `$${parsedFilters.min_price} - $${parsedFilters.max_price}`;
      } else if (parsedFilters.min_price !== undefined) {
        priceStr = `> $${parsedFilters.min_price}`;
      } else if (parsedFilters.max_price !== undefined) {
        priceStr = `< $${parsedFilters.max_price}`;
      }
      chips.push(
        <span key="price" className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
          💰 {priceStr}
        </span>
      );
    }

    if (parsedFilters.bedrooms !== undefined) {
      chips.push(
        <span key="beds" className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
          🛏️ {parsedFilters.bedrooms} Beds
        </span>
      );
    }

    if (parsedFilters.bathrooms !== undefined) {
      chips.push(
        <span key="baths" className="inline-flex items-center rounded-full bg-cyan-100 px-2.5 py-0.5 text-xs font-medium text-cyan-800">
          🚿 {parsedFilters.bathrooms} Baths
        </span>
      );
    }

    if (parsedFilters.status) {
      chips.push(
        <span key="status" className="inline-flex items-center rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800 capitalize">
          🏷️ {parsedFilters.status.replace("_", " ")}
        </span>
      );
    }

    if (chips.length === 0) {
      return (
        <span className="text-sm text-gray-500 italic">No specific filters parsed</span>
      );
    }

    return <div className="flex flex-wrap gap-2">{chips}</div>;
  };

  return (
    <div className="mt-4 rounded-lg border border-indigo-100 bg-indigo-50/50 p-4 shadow-sm">
      <div className="flex items-start gap-4">
        <div className="flex-1">
          <p className="text-sm font-medium text-indigo-900 mb-3 leading-relaxed">
            {aiSummary}
          </p>
          
          <div className="mt-2">
            {!queryParsed ? (
              <div className="inline-flex items-center text-sm text-amber-700 bg-amber-50 px-3 py-1.5 rounded-md border border-amber-200">
                <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                AI parsing unavailable — showing keyword results
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <span className="text-xs font-medium text-indigo-400 uppercase tracking-wider">Understood Filters:</span>
                {renderChips()}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
