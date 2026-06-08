import type { SearchFilters } from "@/types/search";
import { Sparkles, AlertCircle } from "lucide-react";

interface AiParsedFiltersCardProps {
  queryParsed: boolean;
  parsedFilters?: SearchFilters;
  aiSummary: string;
}

export function AiParsedFiltersCard({
  queryParsed,
  parsedFilters,
  aiSummary,
}: AiParsedFiltersCardProps) {
  if (!queryParsed) {
    return (
      <div className="rounded-lg border bg-yellow-50 p-4 mt-4 mb-6">
        <div className="flex items-center space-x-2 text-yellow-800">
          <AlertCircle className="h-5 w-5" />
          <p className="font-medium text-sm">
            AI parsing unavailable — showing keyword results
          </p>
        </div>
        {aiSummary && <p className="mt-2 text-sm text-yellow-700">{aiSummary}</p>}
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4 mt-4 mb-6 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="space-y-3 w-full">
          <div className="flex items-center space-x-2 text-indigo-600">
            <Sparkles className="h-5 w-5" />
            <h3 className="font-medium">AI Search Results</h3>
          </div>
          
          <p className="text-sm text-muted-foreground">{aiSummary}</p>

          {parsedFilters && Object.keys(parsedFilters).length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              {parsedFilters.location && (
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">
                  Location: {parsedFilters.location}
                </div>
              )}
              {parsedFilters.min_price !== undefined && (
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">
                  Min Price: ${parsedFilters.min_price.toLocaleString()}
                </div>
              )}
              {parsedFilters.max_price !== undefined && (
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">
                  Max Price: ${parsedFilters.max_price.toLocaleString()}
                </div>
              )}
              {parsedFilters.bedrooms !== undefined && (
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">
                  Beds: {parsedFilters.bedrooms}+
                </div>
              )}
              {parsedFilters.bathrooms !== undefined && (
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">
                  Baths: {parsedFilters.bathrooms}+
                </div>
              )}
              {parsedFilters.status && (
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">
                  Status: {parsedFilters.status}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
