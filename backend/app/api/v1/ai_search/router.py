from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.security import get_current_user
from app.schemas.ai_search import AiSearchRequest, AiSearchResult
from app.schemas.auth import UserRead
from app.services.ai_search import ai_search
from app.services.ai_search.service import ai_search_stream


router = APIRouter()


def _encode_sse_event(event: str, data: BaseModel) -> str:
    return f"event: {event}\ndata: {data.model_dump_json()}\n\n"


@router.post("", response_model=AiSearchResult)
async def search_properties_with_ai(
    data: AiSearchRequest,
    current_user: UserRead = Depends(get_current_user),
) -> AiSearchResult:
    del current_user
    return ai_search(data.query, data.page, data.page_size)


@router.get("/stream")
async def stream_properties_with_ai(
    query: str,
    page: int = 1,
    page_size: int = 20,
    current_user: UserRead = Depends(get_current_user),
) -> StreamingResponse:
    del current_user

    def _event_stream():
        # Padding comment to exceed ALB/proxy buffer thresholds and force immediate flush.
        # Without this, load balancers buffer small initial chunks until the stream closes.
        yield ": " + " " * 32768 + "\n\n"
        for event, data in ai_search_stream(query, page, page_size):
            yield _encode_sse_event(event, data)

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
