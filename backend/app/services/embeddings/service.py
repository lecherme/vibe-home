import logging
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings
from app.core.supabase import get_supabase_client

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)

_EMBEDDING_DIMENSION = 1536


def _get_openai_client() -> Any:
    settings = get_settings()
    if not settings.embedding_api_key:
        raise RuntimeError("EMBEDDING_API_KEY is not configured")
    if OpenAI is None:
        raise RuntimeError("openai package is not installed")
    return OpenAI(
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
    )


def _build_embedding_text(title: str, description: str, location: str) -> str:
    return f"{title}. {description}. Located in {location}."


def embed_text(text: str) -> list[float]:
    settings = get_settings()
    response = _get_openai_client().embeddings.create(
        model=settings.embedding_model,
        input=text,
        dimensions=_EMBEDDING_DIMENSION,
    )
    embedding = list(response.data[0].embedding)
    if len(embedding) != _EMBEDDING_DIMENSION:
        raise RuntimeError(
            f"Unexpected embedding dimension: expected {_EMBEDDING_DIMENSION}, got {len(embedding)}"
        )
    return embedding


def try_upsert_property_embedding(
    property_id: str,
    title: str,
    description: str,
    location: str,
) -> None:
    try:
        embedding = embed_text(_build_embedding_text(title, description, location))
        (
            get_supabase_client()
            .table("property_embeddings")
            .upsert(
                {
                    "property_id": property_id,
                    "embedding": embedding,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .execute()
        )
    except Exception:
        logger.warning(
            "Failed to upsert property embedding",
            extra={"property_id": property_id},
            exc_info=True,
        )


def semantic_search(query_embedding: list[float], match_count: int = 50) -> list[str]:
    response = get_supabase_client().rpc(
        "match_property_embeddings",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
        },
    ).execute()
    rows = response.data or []
    return [str(row["property_id"]) for row in rows if row.get("property_id")]
