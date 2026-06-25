from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.search import SearchFilters, SearchResult
from app.schemas.property import Property as PropertyRead


class AiSearchRequest(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)


class SummaryRequest(BaseModel):
    search_request_id: str


class SummaryResponse(BaseModel):
    ai_summary: str


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


class IntentField(BaseModel):
    field: str
    value: Any
    raw: str
    label: str
    filterable: bool


class UserNeed(BaseModel):
    type: Literal["household_size", "quiet_environment", "lifestyle"]
    value: bool | int | str
    raw: str


class SearchNotice(BaseModel):
    type: Literal["tension", "suggestion"]
    message: str
    related_need_type: str | None = None


class InterpretedNeeds(BaseModel):
    needs: list[UserNeed] = Field(default_factory=list)
    notices: list[SearchNotice] = Field(default_factory=list)
    unresolved: list[str] = Field(default_factory=list)


class AiSearchResult(SearchResult):
    parsed_filters: SearchFilters
    ai_summary: str = ""
    search_request_id: str | None = None
    query_parsed: bool
    parsed_constraints: list[ConstraintInfo] = Field(default_factory=list)
    strict_items: list[PropertyRead] = Field(default_factory=list)
    recommended_items: list[PropertyRead] = Field(default_factory=list)
    relaxations: list[RelaxationRecord] = Field(default_factory=list)
    match_reasons: dict[str, list[MatchReason]] = Field(default_factory=dict)
    interpreted_intent: list[IntentField] = Field(default_factory=list)
    interpreted_needs: InterpretedNeeds = Field(default_factory=InterpretedNeeds)
