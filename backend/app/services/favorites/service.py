from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.data.properties import get_by_id
from app.schemas.favorite import FavoriteList, FavoriteRead
from app.schemas.property import Property as PropertyRead


favorites_store: dict[str, set[str]] = {}


def add_favorite(user_id: str, property_id: str) -> FavoriteRead:
    if get_by_id(property_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    user_favorites = favorites_store.setdefault(user_id, set())
    if property_id in user_favorites:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Property already favorited",
        )

    user_favorites.add(property_id)
    return FavoriteRead(
        property_id=property_id,
        user_id=user_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def remove_favorite(user_id: str, property_id: str) -> None:
    user_favorites = favorites_store.get(user_id)
    if user_favorites is None or property_id not in user_favorites:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    user_favorites.remove(property_id)
    if not user_favorites:
        favorites_store.pop(user_id, None)


def is_favorite(user_id: str, property_id: str) -> bool:
    return property_id in favorites_store.get(user_id, set())


def get_user_favorites(user_id: str, page: int, page_size: int) -> FavoriteList:
    favorite_properties: list[PropertyRead] = [
        property_item
        for property_id in favorites_store.get(user_id, set())
        if (property_item := get_by_id(property_id)) is not None
    ]
    favorite_properties.sort(
        key=lambda property_item: property_item.created_at,
        reverse=True,
    )

    total = len(favorite_properties)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    return FavoriteList(
        items=favorite_properties[start_index:end_index],
        total=total,
    )
