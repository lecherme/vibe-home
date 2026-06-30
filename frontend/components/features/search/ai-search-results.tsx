import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { MatchReasonsChips } from "@/components/features/search/match-reasons-chips";
import { RelaxationNotice } from "@/components/features/search/relaxation-notice";
import type { AiSearchResult } from "@/types/ai-search";

interface AiSearchResultsProps {
  result: AiSearchResult;
  favoriteIds: Set<string>;
  isSummaryLoading?: boolean;
}

function PropertyResultGrid({
  items,
  favoriteIds,
  matchReasons,
}: {
  items: AiSearchResult["items"];
  favoriteIds: Set<string>;
  matchReasons: NonNullable<AiSearchResult["match_reasons"]>;
}) {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      {items.map((property) => (
        <div key={property.id} className="space-y-3">
          <PropertyCard
            property={property}
            isFavorited={favoriteIds.has(property.id)}
          />
          <MatchReasonsChips reasons={matchReasons[property.id]} />
        </div>
      ))}
    </div>
  );
}

export function AiSearchResults({
  result,
  favoriteIds,
  isSummaryLoading = false,
}: AiSearchResultsProps) {
  const hasGroupedItems = result.strict_items !== undefined || result.recommended_items !== undefined;
  const strictItems = result.strict_items ?? (hasGroupedItems ? [] : result.items ?? []);
  const recommendedItems = result.recommended_items ?? [];
  const matchReasons = result.match_reasons ?? {};
  const hasItems = strictItems.length > 0 || recommendedItems.length > 0;
  const hasSummary = result.ai_summary.trim().length > 0;

  return (
    <div className="space-y-8">
      <div className="text-sm text-gray-600">Found {result.total} properties</div>

      {(isSummaryLoading || hasSummary) && (
        <section className="space-y-3 rounded-lg border border-indigo-100 bg-indigo-50/50 p-4 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">AI Summary</h2>
          {hasSummary ? (
            <p className="text-sm leading-6 text-gray-700">{result.ai_summary}</p>
          ) : (
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
              <span>Generating AI summary...</span>
            </div>
          )}
        </section>
      )}

      {strictItems.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-900">
              完全符合条件 ({strictItems.length}套)
            </h2>
          </div>
          <PropertyResultGrid
            items={strictItems}
            favoriteIds={favoriteIds}
            matchReasons={matchReasons}
          />
        </section>
      )}

      {recommendedItems.length > 0 && (
        <section className="space-y-4">
          <RelaxationNotice relaxations={result.relaxations} />
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-900">
              推荐匹配 ({recommendedItems.length}套)
            </h2>
          </div>
          <PropertyResultGrid
            items={recommendedItems}
            favoriteIds={favoriteIds}
            matchReasons={matchReasons}
          />
        </section>
      )}

      {!hasItems && (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white py-16 text-center">
          <p className="text-lg font-medium text-gray-600">No properties found matching your AI query.</p>
          <p className="mt-2 text-sm text-gray-400">Try rewording your prompt or making it broader.</p>
        </div>
      )}
    </div>
  );
}
