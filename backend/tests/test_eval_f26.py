import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.schemas.property import Property as PropertyRead
from app.schemas.property import PropertyStatus
from app.schemas.search import SearchFilters
from app.services.ai_search import service as ai_search_service
from app.services.ai_search.service import _normalize_query


EVAL_SET_F16_PATH = Path(__file__).with_name("eval_set.json")
EVAL_SET_F26_PATH = Path(__file__).with_name("eval_set_f26.json")
_RELAXATION_CASE_IDS = {
    "soft_only_subway_and_year",
    "soft_only_built_year",
    "mixed_hard_soft_subway",
    "mixed_hard_soft_built_year",
}


_TEST_PROPERTIES = [
    PropertyRead(
        id="prop_a",
        title="Central Skyline Residence",
        description="Family apartment in Central.",
        price=18000000,
        location="Central",
        bedrooms=4,
        bathrooms=3,
        area_sqm=120,
        built_year=2023,
        subway_distance_m=300,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 10, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_b",
        title="Central Classic Flat",
        description="Older but spacious Central unit.",
        price=17000000,
        location="Central",
        bedrooms=4,
        bathrooms=2,
        area_sqm=118,
        built_year=2014,
        subway_distance_m=320,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 9, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_c",
        title="Central New Tower",
        description="Recently built home in Central.",
        price=17500000,
        location="Central",
        bedrooms=4,
        bathrooms=2,
        area_sqm=116,
        built_year=2022,
        subway_distance_m=900,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 8, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_d",
        title="Western District Home",
        description="Four-bedroom unit in Western.",
        price=16000000,
        location="Western",
        bedrooms=4,
        bathrooms=2,
        area_sqm=125,
        built_year=2024,
        subway_distance_m=350,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 7, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_e",
        title="Western Heritage Apartment",
        description="Older Western District apartment.",
        price=15000000,
        location="Western",
        bedrooms=4,
        bathrooms=2,
        area_sqm=110,
        built_year=2012,
        subway_distance_m=800,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_f",
        title="Central Starter Home",
        description="Smaller Central apartment.",
        price=9000000,
        location="Central",
        bedrooms=2,
        bathrooms=1,
        area_sqm=70,
        built_year=2015,
        subway_distance_m=400,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 5, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_g",
        title="Peak Luxury Villa",
        description="Large hilltop villa.",
        price=26000000,
        location="Peak",
        bedrooms=5,
        bathrooms=4,
        area_sqm=220,
        built_year=2024,
        subway_distance_m=1200,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 4, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_h",
        title="Island Family House",
        description="Older island house with space.",
        price=15000000,
        location="Islands",
        bedrooms=4,
        bathrooms=3,
        area_sqm=130,
        built_year=1990,
        subway_distance_m=3000,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 3, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_i",
        title="Central Mid-Rise",
        description="Three-bedroom Central option.",
        price=14000000,
        location="Central",
        bedrooms=3,
        bathrooms=2,
        area_sqm=100,
        built_year=2013,
        subway_distance_m=700,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    ),
    PropertyRead(
        id="prop_j",
        title="Happy Valley Renovated Flat",
        description="Renovated four-bedroom home.",
        price=14800000,
        location="Happy Valley",
        bedrooms=4,
        bathrooms=2,
        area_sqm=108,
        built_year=2019,
        subway_distance_m=480,
        tags=[],
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    ),
]
_PROPERTIES_BY_ID = {property_item.id: property_item for property_item in _TEST_PROPERTIES}


def _load_eval_set_f26() -> list[dict[str, Any]]:
    return json.loads(EVAL_SET_F26_PATH.read_text(encoding="utf-8"))


def _load_eval_set_f16() -> list[dict[str, Any]]:
    return json.loads(EVAL_SET_F16_PATH.read_text(encoding="utf-8"))


def _sorted_properties() -> list[PropertyRead]:
    return sorted(
        _TEST_PROPERTIES,
        key=lambda property_item: property_item.created_at,
        reverse=True,
    )


def _mock_search(filters: SearchFilters, db_session: Any) -> list[str]:
    del db_session
    return [
        property_item.id
        for property_item in _sorted_properties()
        if ai_search_service._matches_filters(property_item, filters)
    ]


def _filters_from_case(case: dict[str, Any]) -> SearchFilters:
    filters_payload = case.get("parsed_filters", case.get("expected_filters", {}))
    assert isinstance(filters_payload, dict)
    return SearchFilters(**filters_payload)


def _item_ids(items: list[PropertyRead]) -> list[str]:
    return [item.id for item in items]


def _expected_split(query: str, filters: SearchFilters) -> tuple[list[str], list[str], SearchFilters]:
    strict_result_ids = ai_search_service._resolve_result_ids(
        query,
        filters,
        query_parsed=True,
    )
    strict_ids = [
        property_id
        for property_id in strict_result_ids
        if (
            (property_item := _PROPERTIES_BY_ID.get(property_id)) is not None
            and ai_search_service._matches_hard_constraints(property_item, filters)
            and ai_search_service._matches_filters(property_item, filters)
        )
    ]
    recommended_ids: list[str] = []
    relaxed_filters = filters
    strict_count = len(strict_ids)
    if strict_count == 0 or strict_count < ai_search_service._RELAX_SUPPLEMENT_THRESHOLD:
        relaxed_result_ids, relaxed_filters, _ = ai_search_service._apply_relaxation(
            query,
            filters,
            True,
        )
        seen_ids = set(strict_ids)
        for property_id in relaxed_result_ids:
            if property_id in seen_ids:
                continue
            property_item = _PROPERTIES_BY_ID.get(property_id)
            if property_item is None:
                continue
            if not ai_search_service._matches_hard_constraints(property_item, filters):
                continue
            if not ai_search_service._matches_filters(property_item, relaxed_filters):
                continue
            if ai_search_service._matches_filters(property_item, filters):
                continue
            recommended_ids.append(property_id)
            seen_ids.add(property_id)
    return strict_ids, recommended_ids, relaxed_filters


def _patch_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    case: dict[str, Any],
) -> SearchFilters | None:
    monkeypatch.setattr(
        ai_search_service,
        "_is_property_search",
        lambda query: case["case_type"] != "non_search",
    )
    monkeypatch.setattr(
        ai_search_service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-embedding-key", llm_api_key="test-llm-key"),
    )
    monkeypatch.setattr(ai_search_service, "get_all", lambda: list(_TEST_PROPERTIES))
    monkeypatch.setattr(ai_search_service, "get_by_id", lambda property_id: _PROPERTIES_BY_ID.get(property_id))
    monkeypatch.setattr(ai_search_service, "search", _mock_search)
    monkeypatch.setattr(ai_search_service, "embed_text", lambda query: query)
    semantic_ids = list(case.get("semantic_ids", []))
    monkeypatch.setattr(
        ai_search_service,
        "semantic_search",
        lambda embedded_query: list(semantic_ids) if embedded_query == case["query"] else [],
    )
    monkeypatch.setattr(
        ai_search_service,
        "_generate_summary",
        lambda query, parsed_filters, total, items, relaxed_conditions=[]: f"summary:{query}:{total}",
    )

    parse_mode = case["parse_mode"]
    if parse_mode == "stub":
        filters = _filters_from_case(case)
        monkeypatch.setattr(
            ai_search_service,
            "_parse_filters",
            lambda query: (filters.model_copy(), True),
        )
        return filters

    if parse_mode == "live":
        response_body = json.dumps(case["llm_response"], ensure_ascii=False)

        def _complete_stub(*args: Any, **kwargs: Any) -> str:
            prompt = kwargs.get("prompt", args[0] if args else "")
            assert case["query"] in prompt
            return response_body

        monkeypatch.setattr(ai_search_service, "complete", _complete_stub)
        return _filters_from_case(case)

    return None


def test_eval_set_f26_has_minimum_coverage() -> None:
    eval_set = _load_eval_set_f26()

    assert len(eval_set) >= 10

    counts = Counter(case["case_type"] for case in eval_set)
    assert counts["hard_only"] >= 2
    assert counts["soft_only"] >= 2
    assert counts["mixed_hard_soft"] >= 2
    assert counts["chinese_vocabulary"] >= 1
    assert counts["no_relax"] >= 1
    assert counts["zero_after_relax"] >= 1
    assert counts["non_search"] >= 1


@pytest.mark.parametrize("case", _load_eval_set_f26(), ids=lambda case: str(case["id"]))
def test_ai_search_meets_f26_contract(
    case: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_filters = _patch_dependencies(monkeypatch, case)

    result = ai_search_service.ai_search(case["query"], page=1, page_size=20)

    assert _item_ids(result.items) == [*_item_ids(result.strict_items), *_item_ids(result.recommended_items)]
    assert result.total == len(result.strict_items) + len(result.recommended_items)

    if case["case_type"] == "non_search":
        assert result.query_parsed is False
        assert result.strict_items == []
        assert result.recommended_items == []
        assert result.relaxations == []
        assert result.match_reasons == {}
        return

    assert expected_filters is not None
    assert result.query_parsed is True
    assert result.parsed_filters.model_dump() == expected_filters.model_dump()
    assert [record.model_dump(mode="python") for record in result.relaxations] == case["expected_relaxations"]
    assert [constraint.model_dump(mode="python") for constraint in result.parsed_constraints] == [
        constraint.model_dump(mode="python")
        for constraint in ai_search_service._build_parsed_constraints(expected_filters)
    ]

    expected_strict_ids, expected_recommended_ids, relaxed_filters = _expected_split(
        case["query"],
        expected_filters,
    )
    assert _item_ids(result.strict_items) == expected_strict_ids
    assert _item_ids(result.recommended_items) == expected_recommended_ids

    for property_item in result.strict_items:
        assert ai_search_service._matches_hard_constraints(property_item, expected_filters)
        assert ai_search_service._matches_filters(property_item, expected_filters)

    for property_item in result.recommended_items:
        assert ai_search_service._matches_hard_constraints(property_item, expected_filters)
        assert ai_search_service._matches_filters(property_item, relaxed_filters)
        assert not ai_search_service._matches_filters(property_item, expected_filters)

    for property_item in result.items:
        reasons = result.match_reasons[property_item.id]
        assert [reason.field for reason in reasons] == [
            field for field, _ in ai_search_service._active_constraint_items(expected_filters)
        ]
        if property_item.id in _item_ids(result.strict_items):
            assert all(reason.matched for reason in reasons)
        elif result.relaxations:
            assert any((not reason.matched) and reason.strength == "soft" for reason in reasons)

    if case["id"] in _RELAXATION_CASE_IDS:
        assert result.relaxations
        recomputed_relaxed_ids, recomputed_recommended_ids, recomputed_filters = _expected_split(
            case["query"],
            expected_filters,
        )
        assert _item_ids(result.strict_items) == recomputed_relaxed_ids
        assert _item_ids(result.recommended_items) == recomputed_recommended_ids
        for record in result.relaxations:
            assert record.from_value == getattr(expected_filters, record.field)
            assert record.to_value == getattr(recomputed_filters, record.field)


def test_f26_strict_items_never_violate_hard_constraints(
) -> None:
    violations: list[str] = []

    for case in _load_eval_set_f26():
        with pytest.MonkeyPatch.context() as monkeypatch:
            expected_filters = _patch_dependencies(monkeypatch, case)
            result = ai_search_service.ai_search(case["query"], page=1, page_size=20)
            if expected_filters is None:
                continue
            for property_item in result.strict_items:
                if not ai_search_service._matches_hard_constraints(property_item, expected_filters):
                    violations.append(f"{case['id']}:{property_item.id}")

    assert violations == []


def test_f16_eval_set_still_passes_30_of_30() -> None:
    eval_set = _load_eval_set_f16()
    failures: list[str] = []

    assert len(eval_set) == 30

    for case in eval_set:
        query = case["query"]
        expected = case["expected"]
        assert isinstance(query, str)
        assert isinstance(expected, dict)

        normalized = _normalize_query(query)
        mismatches = [
            f"{field}: expected {expected_value}, got {normalized.get(field)}"
            for field, expected_value in expected.items()
            if expected_value is not None and normalized.get(field) != expected_value
        ]
        if mismatches:
            failures.append(f"{query} -> {'; '.join(mismatches)}")

    assert failures == []
