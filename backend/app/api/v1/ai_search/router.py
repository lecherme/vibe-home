from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.ai_search import AiSearchRequest, AiSearchResult
from app.schemas.auth import UserRead
from app.services.ai_search import ai_search


router = APIRouter()


@router.post("", response_model=AiSearchResult)
async def search_properties_with_ai(
    data: AiSearchRequest,
    current_user: UserRead = Depends(get_current_user),
) -> AiSearchResult:
    del current_user
    return ai_search(data.query, data.page, data.page_size)
