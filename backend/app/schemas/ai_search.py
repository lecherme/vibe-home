from pydantic import BaseModel, Field

from app.schemas.search import SearchFilters, SearchResult


class AiSearchRequest(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)


class AiSearchResult(SearchResult):
    parsed_filters: SearchFilters
    ai_summary: str
    query_parsed: bool
