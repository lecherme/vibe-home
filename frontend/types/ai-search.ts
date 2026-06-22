import type { Property } from "@/types/property";
import type { SearchFilters, SearchResult } from "@/types/search";

export type ConstraintStrength = "hard" | "soft";

export interface RelaxationRecord {
  field: string;
  from_value: unknown;
  to_value: unknown;
}

export interface MatchReason {
  field: string;
  label: string;
  matched: boolean;
  strength: ConstraintStrength;
}

export interface ConstraintInfo {
  field: string;
  value: unknown;
  strength: ConstraintStrength;
  label: string;
}

export interface AiSearchResult extends SearchResult {
  parsed_filters: SearchFilters;
  ai_summary: string;
  query_parsed: boolean;
  parsed_constraints?: ConstraintInfo[];
  strict_items?: Property[];
  recommended_items?: Property[];
  relaxations?: RelaxationRecord[];
  match_reasons?: Record<string, MatchReason[]>;
}
