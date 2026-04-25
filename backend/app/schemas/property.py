from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
    images: list[str]
    status: PropertyStatus
    created_at: datetime


class PropertyListResponse(BaseModel):
    items: list[Property]
    total: int
    page: int
    page_size: int
