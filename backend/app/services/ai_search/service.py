import json
import logging
import re
from typing import Any

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.data.properties import get_all, get_by_id
from app.schemas.ai_search import AiSearchResult
from app.schemas.property import Property as PropertyRead
from app.schemas.property import PropertyStatus
from app.schemas.search import SearchFilters
from app.services.embeddings.service import embed_text, semantic_search
from app.services.llm import complete
from app.services.search import search


logger = logging.getLogger(__name__)

_SEARCH_MAX_PAGE_SIZE = 100
_HYBRID_MIN_RESULTS = 5
_ALLOWED_STATUS_VALUES = {status.value for status in PropertyStatus}


def _has_filters(filters: SearchFilters) -> bool:
    return any(value is not None for value in filters.model_dump().values())


def _sanitize_json_payload(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    return match.group(0) if match is not None else cleaned


def _normalize_filters(raw_filters: dict[str, Any]) -> SearchFilters:
    normalized_location = raw_filters.get("location")
    if isinstance(normalized_location, str):
        normalized_location = normalized_location.strip() or None
    else:
        normalized_location = None

    normalized_status = raw_filters.get("status")
    if isinstance(normalized_status, str):
        normalized_status = normalized_status.strip().lower() or None
    else:
        normalized_status = None
    if normalized_status not in _ALLOWED_STATUS_VALUES:
        normalized_status = None

    def _to_int(value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    return SearchFilters(
        location=normalized_location,
        min_price=_to_int(raw_filters.get("min_price")),
        max_price=_to_int(raw_filters.get("max_price")),
        bedrooms=_to_int(raw_filters.get("bedrooms")),
        bathrooms=_to_int(raw_filters.get("bathrooms")),
        status=normalized_status,
    )


def _parse_filters(query: str) -> tuple[SearchFilters, bool]:
    prompt = (
        "Extract structured real-estate search filters from the user's query. "
        "All prices are in HKD (Hong Kong Dollars). "
        "Return JSON only with keys location, min_price, max_price, bedrooms, bathrooms, status. "
        "Use null when a value is not present. status must be one of available, sold, rented or null. "
        "For 'more than X bedrooms/bathrooms', return X+1 as an integer.\n"
        f"Query: {query}"
    )
    response_text = complete(prompt=prompt, max_tokens=200, temperature=0, json_mode=True)
    parsed_payload = json.loads(_sanitize_json_payload(response_text))
    if not isinstance(parsed_payload, dict):
        raise ValueError("LLM returned a non-object JSON payload")
    return _normalize_filters(parsed_payload), True


def _keyword_fallback_search(query: str) -> list[str]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return []

    sorted_properties = sorted(
        get_all(),
        key=lambda property_item: property_item.created_at,
        reverse=True,
    )
    return [
        property_item.id
        for property_item in sorted_properties
        if normalized_query in property_item.title.lower()
        or normalized_query in property_item.location.lower()
    ]


def _collect_items(property_ids: list[str], page: int, page_size: int) -> tuple[list[PropertyRead], int]:
    total = len(property_ids)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    items = [
        property_item
        for property_id in property_ids[start_index:end_index]
        if (property_item := get_by_id(property_id)) is not None
    ]
    return items, total


def _generate_summary(
    query: str,
    parsed_filters: SearchFilters,
    total: int,
    items: list[PropertyRead],
) -> str:
    properties_summary = [
        {
            "title": item.title,
            "location": item.location,
            "price": item.price,
            "status": item.status.value,
        }
        for item in items[:5]
    ]
    prompt = (
        "Write exactly one concise sentence summarizing the property search results. "
        "Do not use bullets or multiple sentences.\n"
        f"User query: {query}\n"
        f"Parsed filters: {parsed_filters.model_dump_json()}\n"
        f"Total matches: {total}\n"
        f"Current page results: {json.dumps(properties_summary)}"
    )
    summary = complete(prompt=prompt, max_tokens=80, temperature=0.2)
    if not summary:
        raise ValueError("LLM returned an empty summary")
    return summary


def _resolve_result_ids(
    query: str,
    parsed_filters: SearchFilters,
    *,
    query_parsed: bool,
) -> list[str]:
    if not query_parsed:
        return _keyword_fallback_search(query)

    filter_ids = search(parsed_filters, db_session=None)
    if not query.strip():
        return filter_ids

    semantic_ids: list[str] = []
    semantic_search_failed = False
    try:
        semantic_ids = semantic_search(embed_text(query))
    except Exception:
        semantic_search_failed = True
        logger.warning("Semantic search failed", extra={"query": query}, exc_info=True)

    if semantic_ids:
        filter_id_set = set(filter_ids)
        merged_ids = [property_id for property_id in semantic_ids if property_id in filter_id_set]
        if len(merged_ids) < _HYBRID_MIN_RESULTS:
            seen_ids = set(merged_ids)
            for property_id in filter_ids:
                if property_id not in seen_ids:
                    merged_ids.append(property_id)
                    seen_ids.add(property_id)
        return merged_ids

    if semantic_search_failed:
        return filter_ids

    if _has_filters(parsed_filters):
        return filter_ids

    return _keyword_fallback_search(query)


def ai_search(query: str, page: int, page_size: int) -> AiSearchResult:
    settings = get_settings()
    if not settings.embedding_api_key or not settings.llm_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI search is unavailable",
        )

    try:
        parsed_filters, query_parsed = _parse_filters(query)
    except Exception:
        logger.warning("AI query parsing failed", extra={"query": query}, exc_info=True)
        parsed_filters = SearchFilters()
        query_parsed = False

    resolved_page = max(page, 1)
    resolved_page_size = min(max(page_size, 1), _SEARCH_MAX_PAGE_SIZE)
    result_ids = _resolve_result_ids(
        query,
        parsed_filters,
        query_parsed=query_parsed,
    )
    items, total = _collect_items(result_ids, resolved_page, resolved_page_size)

    try:
        ai_summary = _generate_summary(query, parsed_filters, total, items)
    except Exception:
        logger.warning("AI summary generation failed", extra={"query": query}, exc_info=True)
        ai_summary = f"Found {total} properties matching your search."

    return AiSearchResult(
        items=items,
        total=total,
        page=resolved_page,
        page_size=resolved_page_size,
        parsed_filters=parsed_filters,
        ai_summary=ai_summary,
        query_parsed=query_parsed,
    )
