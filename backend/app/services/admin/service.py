from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.supabase import get_supabase_client
from app.data.properties import get_by_id
from app.schemas.admin import PropertyCreate, PropertyUpdate
from app.schemas.property import Property as PropertyRead
from app.schemas.property import PropertyStatus


def _build_images(image_url: str) -> list[str]:
    return [image_url] if image_url else []


def create_property(data: PropertyCreate) -> PropertyRead:
    property_id = f"prop_{uuid4().hex}"
    while get_by_id(property_id) is not None:
        property_id = f"prop_{uuid4().hex}"

    property_item = PropertyRead(
        id=property_id,
        title=data.title,
        description=data.description,
        price=data.price,
        location=data.location,
        bedrooms=data.bedrooms,
        bathrooms=data.bathrooms,
        area_sqm=data.area,
        images=_build_images(data.image_url),
        status=PropertyStatus.AVAILABLE,
        created_at=datetime.now(timezone.utc),
    )
    get_supabase_client().table("properties").insert(property_item.model_dump(mode="json")).execute()
    return property_item.model_copy(deep=True)


def update_property(property_id: str, data: PropertyUpdate) -> PropertyRead:
    current_property = get_by_id(property_id)
    if current_property is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    updates = data.model_dump(exclude_unset=True)
    updated_values = current_property.model_dump()

    if "title" in updates and updates["title"] is not None:
        updated_values["title"] = updates["title"]
    if "description" in updates and updates["description"] is not None:
        updated_values["description"] = updates["description"]
    if "price" in updates and updates["price"] is not None:
        updated_values["price"] = updates["price"]
    if "location" in updates and updates["location"] is not None:
        updated_values["location"] = updates["location"]
    if "bedrooms" in updates and updates["bedrooms"] is not None:
        updated_values["bedrooms"] = updates["bedrooms"]
    if "bathrooms" in updates and updates["bathrooms"] is not None:
        updated_values["bathrooms"] = updates["bathrooms"]
    if "area" in updates and updates["area"] is not None:
        updated_values["area_sqm"] = updates["area"]
    if "image_url" in updates and updates["image_url"] is not None:
        updated_values["images"] = _build_images(updates["image_url"])

    updated_property = PropertyRead(**updated_values)
    (
        get_supabase_client()
        .table("properties")
        .update(updated_property.model_dump(mode="json"))
        .eq("id", property_id)
        .execute()
    )
    return updated_property.model_copy(deep=True)


def delete_property(property_id: str) -> None:
    if get_by_id(property_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    get_supabase_client().table("properties").delete().eq("id", property_id).execute()
