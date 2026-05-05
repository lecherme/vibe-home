from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.supabase import get_supabase_client
from app.data.properties import get_by_id
from app.schemas.favorite import FavoriteList, FavoriteRead
from app.schemas.property import Property as PropertyRead



def _favorite_exists(user_id: str, property_id: str) -> bool:
    response = (
        get_supabase_client()
        .table("favorites")
        .select("*")
        .eq("user_id", user_id)
        .eq("property_id", property_id)
        .limit(1)
        .execute()
    )
    return bool(response.data)


def add_favorite(user_id: str, property_id: str) -> FavoriteRead:
    if get_by_id(property_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    if _favorite_exists(user_id, property_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Property already favorited",
        )

    favorite = FavoriteRead(
        property_id=property_id,
        user_id=user_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    get_supabase_client().table("favorites").insert(favorite.model_dump()).execute()
    return favorite


def remove_favorite(user_id: str, property_id: str) -> None:
    if not _favorite_exists(user_id, property_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    (
        get_supabase_client()
        .table("favorites")
        .delete()
        .eq("user_id", user_id)
        .eq("property_id", property_id)
        .execute()
    )


def is_favorite(user_id: str, property_id: str) -> bool:
    return _favorite_exists(user_id, property_id)


def get_user_favorites(user_id: str, page: int, page_size: int) -> FavoriteList:
    response = (
        get_supabase_client()
        .table("favorites")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    favorite_properties: list[PropertyRead] = [
        property_item
        for property_id in [row["property_id"] for row in response.data]
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
