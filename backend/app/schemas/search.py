from app.schemas.property import Property as PropertyRead
from app.schemas.property import PropertyStatus
from pydantic import BaseModel
from typing import Optional


class SearchFilters(BaseModel):
    location: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    area_min: Optional[int] = None
    area_max: Optional[int] = None
    bedrooms_min: Optional[int] = None
    bedrooms_max: Optional[int] = None
    bathrooms_min: Optional[int] = None
    bathrooms_max: Optional[int] = None
    built_year_min: Optional[int] = None
    subway_distance_max: Optional[int] = None
    status: Optional[PropertyStatus] = None


class SearchResult(BaseModel):
    items: list[PropertyRead]
    total: int
    page: int
    page_size: int
