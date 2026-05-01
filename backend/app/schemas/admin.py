from typing import Optional

from pydantic import BaseModel


class PropertyCreate(BaseModel):
    title: str
    description: str
    price: float
    location: str
    bedrooms: int
    bathrooms: int
    area: float
    image_url: str = ""


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    image_url: Optional[str] = None
