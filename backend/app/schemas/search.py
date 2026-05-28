from app.schemas.property import Property as PropertyRead
from pydantic import BaseModel
from typing import Optional


class SearchFilters(BaseModel):
    location: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = None


class SearchResult(BaseModel):
    items: list[PropertyRead]
    total: int
    page: int
    page_size: int
