from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.auth import UserRead


router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user
