from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.core.security import get_current_user
from app.data.properties import get_all, get_by_id
from app.schemas.property import Property, PropertyListResponse, PropertyStatus
from app.schemas.search import SearchFilters, SearchResult
from app.schemas.auth import UserRead
from app.services.search import search


router = APIRouter()

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 12
MAX_PAGE_SIZE = 50
SEARCH_DEFAULT_PAGE_SIZE = 20
SEARCH_MAX_PAGE_SIZE = 100


@router.get("", response_model=PropertyListResponse)
async def list_properties(
    page: int = Query(default=DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1),
    current_user: UserRead = Depends(get_current_user),
) -> PropertyListResponse:
    del current_user

    resolved_page_size = min(page_size, MAX_PAGE_SIZE)
    sorted_properties = sorted(
        get_all(),
        key=lambda property_item: property_item.created_at,
        reverse=True,
    )
    total = len(sorted_properties)
    start_index = (page - 1) * resolved_page_size
    end_index = start_index + resolved_page_size

    return PropertyListResponse(
        items=sorted_properties[start_index:end_index],
        total=total,
        page=page,
        page_size=resolved_page_size,
    )


@router.get("/search", response_model=SearchResult)
async def search_properties(
    location: Optional[str] = Query(default=None),
    min_price: Optional[int] = Query(default=None, ge=0),
    max_price: Optional[int] = Query(default=None, ge=0),
    bedrooms: Optional[int] = Query(default=None, ge=0),
    bathrooms: Optional[int] = Query(default=None, ge=0),
    status_filter: Optional[PropertyStatus] = Query(default=None, alias="status"),
    page: int = Query(default=DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=SEARCH_DEFAULT_PAGE_SIZE, ge=1),
    current_user: UserRead = Depends(get_current_user),
) -> SearchResult:
    del current_user

    filters = SearchFilters(
        location=location,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        status=status_filter.value if status_filter is not None else None,
    )
    matching_property_ids = search(filters, db_session=None)
    resolved_page_size = min(page_size, SEARCH_MAX_PAGE_SIZE)
    total = len(matching_property_ids)
    start_index = (page - 1) * resolved_page_size
    end_index = start_index + resolved_page_size

    items = [
        property_item
        for property_id in matching_property_ids[start_index:end_index]
        if (property_item := get_by_id(property_id)) is not None
    ]

    return SearchResult(
        items=items,
        total=total,
        page=page,
        page_size=resolved_page_size,
    )


@router.get("/{property_id}", response_model=Property)
async def get_property(
    property_id: str,
    current_user: UserRead = Depends(get_current_user),
) -> Property:
    del current_user

    property_item = get_by_id(property_id)
    if property_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    return property_item
