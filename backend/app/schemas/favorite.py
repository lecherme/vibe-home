from app.schemas.property import Property as PropertyRead
from pydantic import BaseModel


class FavoriteRead(BaseModel):
    property_id: str
    user_id: str
    created_at: str


class FavoriteList(BaseModel):
    items: list[PropertyRead]
    total: int


class FavoriteStatus(BaseModel):
    is_favorite: bool
