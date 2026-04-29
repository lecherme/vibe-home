from typing import Any

from app.data.properties import get_all
from app.schemas.search import SearchFilters


def search(filters: SearchFilters, db_session: Any) -> list[str]:
    del db_session

    normalized_location = filters.location.strip().lower() if filters.location else None
    filter_status = getattr(filters.status, "value", filters.status)
    matching_property_ids: list[str] = []

    sorted_properties = sorted(
        get_all(),
        key=lambda property_item: property_item.created_at,
        reverse=True,
    )
    for property_item in sorted_properties:
        if (
            normalized_location is not None
            and normalized_location not in property_item.location.lower()
        ):
            continue

        if filters.min_price is not None and property_item.price < filters.min_price:
            continue

        if filters.max_price is not None and property_item.price > filters.max_price:
            continue

        if filters.bedrooms is not None and property_item.bedrooms < filters.bedrooms:
            continue

        if filter_status is not None and property_item.status.value != filter_status:
            continue

        matching_property_ids.append(property_item.id)

    return matching_property_ids
