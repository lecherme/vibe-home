import json
from unittest.mock import patch

import pytest

from app.core.config import get_settings
from app.schemas.search import SearchFilters
from app.services.ai_search.service import _parse_filters


try:
    _SETTINGS = get_settings()
except Exception:  # pragma: no cover - environment-dependent
    _SETTINGS = None


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        _SETTINGS is None or not _SETTINGS.llm_api_key,
        reason="requires configured LLM API key",
    ),
]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("两个浴室太少", SearchFilters(bathrooms_min=3)),
        ("三个卧室不够用", SearchFilters(bedrooms_min=4)),
        ("4个卧室太多", SearchFilters(bedrooms_max=3)),
        ("2 bedrooms not enough", SearchFilters(bedrooms_min=3)),
        ("5 bathrooms too many", SearchFilters(bathrooms_max=4)),
        ("两个卧室太少 预算2000万", SearchFilters(bedrooms_min=3, max_price=20000000)),
        ("3间卧室不够 预算1500w", SearchFilters(bedrooms_min=4, max_price=15000000)),
        ("一个浴室不够用 两间卧室太少", SearchFilters(bathrooms_min=2, bedrooms_min=3)),
    ],
)
def test_parse_filters_subjective_room_cases(query: str, expected: SearchFilters) -> None:
    parsed_filters, query_parsed = _parse_filters(query)

    assert query_parsed is True
    assert parsed_filters.model_dump() == expected.model_dump()


def test_llm_forbidden_bound_keys_are_stripped() -> None:
    """LLM returning bedrooms_min/max directly must not set filter bounds."""
    forbidden_response = json.dumps({
        "location": None,
        "status": None,
        "remainder": None,
        "bedrooms_min": 99,
        "bedrooms_max": 88,
        "bathrooms_min": 77,
        "bathrooms_max": 66,
        "bedrooms_subjective_label": None,
        "bedrooms_ref": None,
        "bathrooms_subjective_label": None,
        "bathrooms_ref": None,
    })
    with patch("app.services.ai_search.service.complete", return_value=forbidden_response):
        parsed_filters, query_parsed = _parse_filters("Central")

    assert parsed_filters.bedrooms_min is None
    assert parsed_filters.bedrooms_max is None
    assert parsed_filters.bathrooms_min is None
    assert parsed_filters.bathrooms_max is None
