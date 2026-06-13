from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    RENTED = "rented"


class Property(BaseModel):
    id: str
    title: str
    description: str
    price: float
    location: str
    bedrooms: int
    bathrooms: int
    area_sqm: float
    built_year: int | None = None
    subway_distance_m: int | None = None
    tags: list[str] = Field(default_factory=list)
    images: list[str]
    status: PropertyStatus
    created_at: datetime


class PropertyListResponse(BaseModel):
    items: list[Property]
    total: int
    page: int
    page_size: int
