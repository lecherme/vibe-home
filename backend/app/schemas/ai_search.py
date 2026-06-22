from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.search import SearchFilters, SearchResult
from app.schemas.property import Property as PropertyRead


class AiSearchRequest(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)


class RelaxationRecord(BaseModel):
    field: str
    from_value: Any
    to_value: Any


class MatchReason(BaseModel):
    field: str
    label: str
    matched: bool
    strength: Literal["hard", "soft"]


class ConstraintInfo(BaseModel):
    field: str
    value: Any
    strength: Literal["hard", "soft"]
    label: str


class AiSearchResult(SearchResult):
    parsed_filters: SearchFilters
    ai_summary: str
    query_parsed: bool
    parsed_constraints: list[ConstraintInfo] = Field(default_factory=list)
    strict_items: list[PropertyRead] = Field(default_factory=list)
    recommended_items: list[PropertyRead] = Field(default_factory=list)
    relaxations: list[RelaxationRecord] = Field(default_factory=list)
    match_reasons: dict[str, list[MatchReason]] = Field(default_factory=dict)
