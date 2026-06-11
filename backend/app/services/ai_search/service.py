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
_PRICE_UNIT_PATTERN = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>w|万)", re.IGNORECASE)
_PRICE_SUFFIX_PATTERN = r"(?:\s*(?:hkd|hk\$))?"
_BEDROOM_PATTERN = r"(?:卧室|房间|bedrooms?|beds?)"
_BATHROOM_PATTERN = r"(?:卫生间|洗手间|浴室|bathrooms?|baths?)"
_ROOM_SUFFIX_BLOCKER = rf"(?!\s*(?:个|间)?\s*(?:{_BEDROOM_PATTERN}|{_BATHROOM_PATTERN}))"
_MIN_COMPARATORS = {"以上", "至少", "最少", "at least", "or more", "or above"}
_GREATER_THAN_COMPARATORS = {"more than", "greater than", "超过"}
_MAX_COMPARATORS = {"以下", "at most", "不超过", "or below"}
_LESS_THAN_COMPARATORS = {"less than", "fewer than", "少于"}
_CHINESE_DIGITS = {"一": "1", "二": "2", "两": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"}
_CHINESE_DIGIT_RE = re.compile("|".join(_CHINESE_DIGITS))


def _has_filters(filters: SearchFilters) -> bool:
    return any(value is not None for value in filters.model_dump().values())


def _sanitize_json_payload(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    return match.group(0) if match is not None else cleaned


def _normalize_query(query: str) -> dict[str, Any]:
    normalized_query = _CHINESE_DIGIT_RE.sub(lambda m: _CHINESE_DIGITS[m.group(0)], query)
    normalized_query = _PRICE_UNIT_PATTERN.sub(
        lambda match: str(int(float(match.group("value")) * 10000)),
        normalized_query,
    )
    extracted: dict[str, int | None] = {
        "min_price": None,
        "max_price": None,
        "bedrooms_min": None,
        "bedrooms_max": None,
        "bathrooms_min": None,
        "bathrooms_max": None,
    }

    def _update_min(key: str, value: int) -> None:
        current = extracted.get(key)
        extracted[key] = value if current is None else max(current, value)

    def _update_max(key: str, value: int) -> None:
        if value < 0:
            return
        current = extracted.get(key)
        extracted[key] = value if current is None else min(current, value)

    remaining_query = normalized_query

    def _extract_prices(pattern: str, field_name: str) -> None:
        nonlocal remaining_query

        def _replace(match: re.Match[str]) -> str:
            price = int(float(match.group("price")))
            if field_name == "min_price":
                _update_min(field_name, price)
            else:
                _update_max(field_name, price)
            return " "

        remaining_query = re.sub(pattern, _replace, remaining_query, flags=re.IGNORECASE)

    _extract_prices(
        rf"(?:预算|budget|不超过|under|below)\s*(?P<price>\d+(?:\.\d+)?){_PRICE_SUFFIX_PATTERN}{_ROOM_SUFFIX_BLOCKER}",
        "max_price",
    )
    _extract_prices(
        rf"(?P<price>\d+(?:\.\d+)?){_PRICE_SUFFIX_PATTERN}{_ROOM_SUFFIX_BLOCKER}\s*(?:以内|以下|预算|budget)",
        "max_price",
    )
    _extract_prices(
        rf"(?:至少|最少|at\s+least)\s*(?P<price>\d+(?:\.\d+)?){_PRICE_SUFFIX_PATTERN}{_ROOM_SUFFIX_BLOCKER}",
        "min_price",
    )

    def _extract_room_bounds(noun_pattern: str, min_key: str, max_key: str) -> None:
        nonlocal remaining_query

        def _apply_comparator(raw_comparator: str, count: int) -> None:
            comparator = " ".join(raw_comparator.lower().split())
            if comparator in _MIN_COMPARATORS:
                _update_min(min_key, count)
            elif comparator in _GREATER_THAN_COMPARATORS:
                _update_min(min_key, count + 1)
            elif comparator in _MAX_COMPARATORS:
                _update_max(max_key, count)
            elif comparator in _LESS_THAN_COMPARATORS:
                _update_max(max_key, count - 1)

        def _replace(match: re.Match[str]) -> str:
            _apply_comparator(match.group("comparator"), int(match.group("count")))
            return " "

        remaining_query = re.sub(
            rf"(?P<comparator>至少|最少|at\s+least|or\s+more|or\s+above|more\s+than|greater\s+than|"
            rf"at\s+most|不超过|or\s+below|less\s+than|fewer\s+than|超过|少于)\s*"
            rf"(?P<count>\d+)\s*(?:个|间)?\s*{noun_pattern}",
            _replace,
            remaining_query,
            flags=re.IGNORECASE,
        )
        remaining_query = re.sub(
            rf"(?P<count>\d+)\s*(?:个|间)?\s*{noun_pattern}\s*"
            rf"(?P<comparator>以上|至少|最少|at\s+least|or\s+more|or\s+above|more\s+than|greater\s+than|"
            rf"以下|at\s+most|不超过|or\s+below|less\s+than|fewer\s+than|超过|少于)",
            _replace,
            remaining_query,
            flags=re.IGNORECASE,
        )
        remaining_query = re.sub(
            rf"(?P<count>\d+)\s*(?:个|间)?\s*(?P<comparator>以上|以下)\s*{noun_pattern}",
            _replace,
            remaining_query,
            flags=re.IGNORECASE,
        )

    _extract_room_bounds(_BEDROOM_PATTERN, "bedrooms_min", "bedrooms_max")
    _extract_room_bounds(_BATHROOM_PATTERN, "bathrooms_min", "bathrooms_max")

    # --- digit-bounded single-char shorthand passes (N室, N卧, N卫) ---
    def _extract_shorthand_comparator(char_noun: str, min_key: str, max_key: str) -> None:
        nonlocal remaining_query

        def _apply_comparator_sh(raw_comparator: str, count: int) -> None:
            comparator = " ".join(raw_comparator.lower().split())
            if comparator in _MIN_COMPARATORS:
                _update_min(min_key, count)
            elif comparator in _GREATER_THAN_COMPARATORS:
                _update_min(min_key, count + 1)
            elif comparator in _MAX_COMPARATORS:
                _update_max(max_key, count)
            elif comparator in _LESS_THAN_COMPARATORS:
                _update_max(max_key, count - 1)

        def _replace_sh(match: re.Match[str]) -> str:
            _apply_comparator_sh(match.group("comparator"), int(match.group("count")))
            return " "

        # comparator before N+char
        remaining_query = re.sub(
            rf"(?P<comparator>至少|最少|at\s+least|or\s+more|or\s+above|more\s+than|greater\s+than|"
            rf"at\s+most|不超过|or\s+below|less\s+than|fewer\s+than|超过|少于)\s*"
            rf"(?P<count>\d+){char_noun}",
            _replace_sh,
            remaining_query,
            flags=re.IGNORECASE,
        )
        # N+char followed by comparator
        remaining_query = re.sub(
            rf"(?P<count>\d+){char_noun}\s*"
            rf"(?P<comparator>以上|至少|最少|at\s+least|or\s+more|or\s+above|more\s+than|greater\s+than|"
            rf"以下|at\s+most|不超过|or\s+below|less\s+than|fewer\s+than|超过|少于)",
            _replace_sh,
            remaining_query,
            flags=re.IGNORECASE,
        )
        # N + 以上/以下 + char
        remaining_query = re.sub(
            rf"(?P<count>\d+)\s*(?P<comparator>以上|以下)\s*{char_noun}",
            _replace_sh,
            remaining_query,
            flags=re.IGNORECASE,
        )

    _extract_shorthand_comparator("室", "bedrooms_min", "bedrooms_max")
    _extract_shorthand_comparator("卧", "bedrooms_min", "bedrooms_max")
    _extract_shorthand_comparator("卫", "bathrooms_min", "bathrooms_max")

    # --- bare room count extraction (no comparator) → sets _min ---
    def _extract_bare_count(pattern: str, min_key: str) -> None:
        nonlocal remaining_query

        def _replace_bare(match: re.Match[str]) -> str:
            _update_min(min_key, int(match.group("count")))
            return " "

        remaining_query = re.sub(pattern, _replace_bare, remaining_query, flags=re.IGNORECASE)

    _SUBJECTIVE_BLOCKER = r"(?!\s*(?:太多|太少|太好|刚好|不够|够用|too\s+many|too\s+few|not\s+enough))"
    # bedroom bare counts
    _extract_bare_count(rf"(?P<count>\d+)\s*(?:个|间)\s*{_BEDROOM_PATTERN}{_SUBJECTIVE_BLOCKER}", "bedrooms_min")
    _extract_bare_count(rf"(?P<count>\d+)室(?!\s*(?:个|间|以上|以下|至少|最少|太多|太少|刚好|不够)){_SUBJECTIVE_BLOCKER}", "bedrooms_min")
    _extract_bare_count(rf"(?P<count>\d+)卧(?!\s*(?:个|间|室|以上|以下|至少|最少)){_SUBJECTIVE_BLOCKER}", "bedrooms_min")
    _extract_bare_count(rf"(?P<count>\d+)\s*(?:bedrooms?|beds?){_SUBJECTIVE_BLOCKER}", "bedrooms_min")
    # bathroom bare counts
    _extract_bare_count(rf"(?P<count>\d+)\s*(?:个|间)\s*{_BATHROOM_PATTERN}{_SUBJECTIVE_BLOCKER}", "bathrooms_min")
    _extract_bare_count(rf"(?P<count>\d+)卫(?!\s*(?:个|间|以上|以下|至少|最少|星|生)){_SUBJECTIVE_BLOCKER}", "bathrooms_min")
    _extract_bare_count(rf"(?P<count>\d+)\s*(?:bathrooms?|baths?){_SUBJECTIVE_BLOCKER}", "bathrooms_min")

    return {
        **extracted,
        "remaining_query": re.sub(r"\s+", " ", remaining_query).strip(" ,，;；"),
    }


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
        bedrooms_min=_to_int(raw_filters.get("bedrooms_min")),
        bedrooms_max=_to_int(raw_filters.get("bedrooms_max")),
        bathrooms_min=_to_int(raw_filters.get("bathrooms_min")),
        bathrooms_max=_to_int(raw_filters.get("bathrooms_max")),
        status=normalized_status,
    )


_LLM_ALLOWED_KEYS = frozenset({
    "location", "status", "remainder",
    "bedrooms_subjective_label", "bedrooms_ref",
    "bathrooms_subjective_label", "bathrooms_ref",
})


def _apply_subjective_room_filters(
    raw_filters: dict[str, Any],
    deterministic_filters: dict[str, Any],
) -> dict[str, Any]:
    sanitized_llm = {k: v for k, v in raw_filters.items() if k in _LLM_ALLOWED_KEYS}
    merged_filters = {**sanitized_llm, **deterministic_filters}

    def _normalize_label(value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip().lower()
        return normalized or None

    def _to_int(value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _apply(label_key: str, ref_key: str, min_key: str, max_key: str) -> None:
        label = _normalize_label(raw_filters.get(label_key))
        ref = _to_int(raw_filters.get(ref_key))
        if ref is None:
            return
        if label == "insufficient" and deterministic_filters.get(min_key) is None:
            merged_filters[min_key] = ref + 1
        elif label == "excessive" and deterministic_filters.get(max_key) is None:
            merged_filters[max_key] = ref - 1

    _apply("bedrooms_subjective_label", "bedrooms_ref", "bedrooms_min", "bedrooms_max")
    _apply("bathrooms_subjective_label", "bathrooms_ref", "bathrooms_min", "bathrooms_max")
    return merged_filters


def _parse_filters(query: str) -> tuple[SearchFilters, bool]:
    if not query.strip():
        return SearchFilters(), True

    normalized_query = _normalize_query(query)
    deterministic_filters = {
        key: value
        for key, value in normalized_query.items()
        if key != "remaining_query" and value is not None
    }
    remaining_query = normalized_query.get("remaining_query", "")
    if not remaining_query:
        return _normalize_filters(deterministic_filters), bool(deterministic_filters)

    system_prompt = (
        "Extract only unresolved real-estate filters from the remaining query text. "
        "Direct filter bounds for price, bedrooms, and bathrooms were already parsed deterministically, so do not "
        "return or infer bedrooms_min, bedrooms_max, bathrooms_min, bathrooms_max, min_price, or max_price. "
        "You may identify subjective room-count judgments only when the user states an explicit bedroom or bathroom "
        "count N together with a judgment. Return JSON only with keys location, status, remainder, "
        "bedrooms_subjective_label, bedrooms_ref, bathrooms_subjective_label, bathrooms_ref. "
        "Allowed subjective labels are insufficient, excessive, adequate, unknown, or null. "
        "If no explicit count is stated for a subjective bedroom or bathroom judgment, set the corresponding ref "
        "to null and label to unknown or null. "
        "Use null when a value is not present. status must be one of available, sold, rented or null."
    )
    user_content = (
        f"Original query: {query}\n"
        f"Resolved numeric filters: {json.dumps(deterministic_filters, ensure_ascii=False)}\n"
        f"Remaining query: {remaining_query}"
    )
    last_exc: Exception = RuntimeError("no attempts made")
    for _ in range(2):
        try:
            response_text = complete(
                prompt=user_content,
                max_tokens=200,
                temperature=0,
                json_mode=True,
                system_prompt=system_prompt,
                disable_thinking=True,
            )
            parsed_payload = json.loads(_sanitize_json_payload(response_text))
            if not isinstance(parsed_payload, dict):
                raise ValueError("LLM returned a non-object JSON payload")
            return _normalize_filters(_apply_subjective_room_filters(parsed_payload, deterministic_filters)), True
        except Exception as exc:
            last_exc = exc
    if deterministic_filters:
        return _normalize_filters(deterministic_filters), True
    raise last_exc


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
