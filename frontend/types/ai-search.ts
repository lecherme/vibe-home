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

export interface IntentField {
  field: string;
  value: unknown;
  raw: string;
  label: string;
  filterable: boolean;
}

export type NeedType = "household_size" | "quiet_environment" | "lifestyle";

export type NoticeType = "tension" | "suggestion";

export interface UserNeed {
  type: NeedType;
  value: number | boolean | string;
  raw: string;
}

export interface SearchNotice {
  type: NoticeType;
  message: string;
  related_need_type: string | null;
}

export interface InterpretedNeeds {
  needs: UserNeed[];
  notices: SearchNotice[];
  unresolved: string[];
}

export interface SearchSummaryRequest {
  search_request_id: string;
}

export interface SearchSummaryResponse {
  ai_summary: string;
}

export interface AiSearchResult extends SearchResult {
  parsed_filters: SearchFilters;
  ai_summary: string;
  search_request_id?: string;
  query_parsed: boolean;
  parsed_constraints?: ConstraintInfo[];
  strict_items?: Property[];
  recommended_items?: Property[];
  relaxations?: RelaxationRecord[];
  match_reasons?: Record<string, MatchReason[]>;
  interpreted_intent?: IntentField[];
  interpreted_needs?: InterpretedNeeds;
}
