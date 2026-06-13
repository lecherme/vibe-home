from typing import Optional

from pydantic import BaseModel, Field


class PropertyCreate(BaseModel):
    title: str
    description: str
    price: float
    location: str
    bedrooms: int
    bathrooms: int
    area: float
    built_year: Optional[int] = None
    subway_distance_m: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    built_year: Optional[int] = None
    subway_distance_m: Optional[int] = None
    tags: Optional[list[str]] = None
    images: Optional[list[str]] = None
