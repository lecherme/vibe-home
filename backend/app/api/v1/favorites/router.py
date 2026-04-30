from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.core.security import get_current_user
from app.schemas.auth import AppRole, UserRead
from app.schemas.favorite import FavoriteList, FavoriteRead, FavoriteStatus
from app.services.favorites import add_favorite, get_user_favorites, remove_favorite
from app.services.favorites.service import is_favorite


router = APIRouter()

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 12
MAX_PAGE_SIZE = 50


async def require_non_admin_user(
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    if current_user.role == AppRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return current_user


@router.post(
    "/{property_id}",
    response_model=FavoriteRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_favorite(
    property_id: str,
    current_user: UserRead = Depends(require_non_admin_user),
) -> FavoriteRead:
    return add_favorite(current_user.id, property_id)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    property_id: str,
    current_user: UserRead = Depends(require_non_admin_user),
) -> Response:
    remove_favorite(current_user.id, property_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=FavoriteList)
async def list_favorites(
    page: int = Query(default=DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1),
    current_user: UserRead = Depends(require_non_admin_user),
) -> FavoriteList:
    resolved_page_size = min(page_size, MAX_PAGE_SIZE)
    return get_user_favorites(
        current_user.id,
        page=page,
        page_size=resolved_page_size,
    )


@router.get("/{property_id}", response_model=FavoriteStatus)
async def get_favorite_status(
    property_id: str,
    current_user: UserRead = Depends(require_non_admin_user),
) -> FavoriteStatus:
    return FavoriteStatus(
        is_favorite=is_favorite(current_user.id, property_id),
    )
