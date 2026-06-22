import { PropertyCard } from "@/components/features/properties/PropertyCard";
import { MatchReasonsChips } from "@/components/features/search/match-reasons-chips";
import { RelaxationNotice } from "@/components/features/search/relaxation-notice";
import type { AiSearchResult } from "@/types/ai-search";

interface AiSearchResultsProps {
  result: AiSearchResult;
  favoriteIds: Set<string>;
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

export function AiSearchResults({ result, favoriteIds }: AiSearchResultsProps) {
  const hasGroupedItems = result.strict_items !== undefined || result.recommended_items !== undefined;
  const strictItems = result.strict_items ?? (hasGroupedItems ? [] : result.items ?? []);
  const recommendedItems = result.recommended_items ?? [];
  const matchReasons = result.match_reasons ?? {};

  return (
    <div className="space-y-8">
      <div className="text-sm text-gray-600">Found {result.total} properties</div>

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
    </div>
  );
}
