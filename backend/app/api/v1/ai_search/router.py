from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.ai_search import AiSearchRequest, AiSearchResult, SummaryRequest, SummaryResponse
from app.schemas.auth import UserRead
from app.services.ai_search.service import ai_search, generate_summary_for_request


router = APIRouter()


@router.post("", response_model=AiSearchResult)
async def search_properties_with_ai(
    data: AiSearchRequest,
    current_user: UserRead = Depends(get_current_user),
) -> AiSearchResult:
    del current_user
    return ai_search(data.query, data.page, data.page_size)


@router.post("/summary", response_model=SummaryResponse)
async def search_properties_with_ai_summary(
    data: SummaryRequest,
    current_user: UserRead = Depends(get_current_user),
) -> SummaryResponse:
    del current_user
    return SummaryResponse(ai_summary=generate_summary_for_request(data.search_request_id))
