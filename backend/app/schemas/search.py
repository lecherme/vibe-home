from app.schemas.property import Property as PropertyRead
from app.schemas.property import PropertyStatus
from pydantic import AliasChoices, BaseModel, Field
from typing import Optional


class SearchFilters(BaseModel):
    location: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    bedrooms_min: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("bedrooms_min", "bedrooms"),
    )
    bedrooms_max: Optional[int] = None
    bathrooms_min: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("bathrooms_min", "bathrooms"),
    )
    bathrooms_max: Optional[int] = None
    status: Optional[PropertyStatus] = None


class SearchResult(BaseModel):
    items: list[PropertyRead]
    total: int
    page: int
    page_size: int
