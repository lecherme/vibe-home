import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.schemas.ai_search import InterpretedNeeds, UserNeed
from app.schemas.search import SearchFilters
from app.services.ai_search import service as ai_search_service


EVAL_SET_F27_PATH = Path(__file__).with_name("eval_set_f27.json")
_NEUTRAL_PARSE_LLM_RESPONSE = json.dumps(
    {
        "location": None,
        "status": None,
        "remainder": None,
        "bedrooms_subjective_label": None,
        "bedrooms_ref": None,
        "bathrooms_subjective_label": None,
        "bathrooms_ref": None,
    },
    ensure_ascii=False,
)


def _load_eval_set_f27() -> list[dict[str, Any]]:
    return json.loads(EVAL_SET_F27_PATH.read_text(encoding="utf-8"))


def _case_by_id(case_id: str) -> dict[str, Any]:
    for case in _load_eval_set_f27():
        if case["id"] == case_id:
            return case
    raise AssertionError(f"missing eval case: {case_id}")


def _filters_from_case(case: dict[str, Any]) -> SearchFilters:
    return SearchFilters(**case.get("parsed_filters", {}))


def _needs_from_case(case: dict[str, Any]) -> list[UserNeed]:
    return [UserNeed(**need) for need in case.get("expected_needs", [])]


def _stub_ai_search_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    parsed_filters: SearchFilters,
    interpreted_needs: InterpretedNeeds,
) -> None:
    monkeypatch.setattr(
        ai_search_service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-key", llm_api_key="test-key"),
    )
    monkeypatch.setattr(ai_search_service, "_parse_filters", lambda query: (parsed_filters, True))
    monkeypatch.setattr(ai_search_service, "_interpret_needs", lambda query, filters: interpreted_needs)
    monkeypatch.setattr(
        ai_search_service,
        "_resolve_result_ids",
        lambda query, filters, **kwargs: ([], None, [], False),
    )
    monkeypatch.setattr(
        ai_search_service,
        "_apply_relaxation",
        lambda query, filters, query_parsed, **kwargs: ([], filters, [], 0),
    )
    monkeypatch.setattr(ai_search_service, "_build_relaxations", lambda original, relaxed: [])
    monkeypatch.setattr(ai_search_service, "_build_parsed_constraints", lambda filters: [])
    monkeypatch.setattr(ai_search_service, "_collect_items", lambda result_ids, page, page_size: ([], 0))
    monkeypatch.setattr(ai_search_service, "_build_match_reasons", lambda items, filters: {})
    monkeypatch.setattr(
        ai_search_service,
        "_generate_summary",
        lambda query, filters, total, items, relaxed_conditions: "summary",
    )


def test_eval_set_f27_has_minimum_coverage() -> None:
    assert len(_load_eval_set_f27()) >= 8


@pytest.mark.parametrize(
    "case_id",
    [
        "bug_026_entry",
        "one_room_two_living_three_person_family",
        "two_room_one_living_three_person_family",
        "three_room_two_living_four_person_family",
        "pure_filters_only",
    ],
)
def test_f27_property_search_and_filter_parsing(monkeypatch: pytest.MonkeyPatch, case_id: str) -> None:
    case = _case_by_id(case_id)
    monkeypatch.setattr(ai_search_service, "complete", lambda *args, **kwargs: _NEUTRAL_PARSE_LLM_RESPONSE)

    assert ai_search_service._is_property_search(case["query"]) is case["expected_property_search"]

    parsed_filters, query_parsed = ai_search_service._parse_filters(case["query"])

    assert query_parsed is True
    assert parsed_filters.model_dump(exclude_none=True) == case["parsed_filters"]


@pytest.mark.parametrize(
    ("case_id", "expected_living_rooms"),
    [
        ("bug_026_entry", 2),
        ("one_room_two_living_three_person_family", 2),
        ("two_room_one_living_three_person_family", 1),
        ("three_room_two_living_four_person_family", 2),
        ("pure_filters_only", None),
    ],
)
def test_extract_living_rooms(case_id: str, expected_living_rooms: int | None) -> None:
    case = _case_by_id(case_id)

    assert ai_search_service._extract_living_rooms(case["query"]) == expected_living_rooms


@pytest.mark.parametrize(
    "case_id",
    [
        "one_room_two_living_three_person_family",
        "two_room_one_living_three_person_family",
        "three_room_two_living_four_person_family",
        "pure_filters_only",
        "elderly_quiet_unresolved",
        "school_and_environment_unresolved",
        "non_search_query",
    ],
)
def test_interpret_needs_cases(monkeypatch: pytest.MonkeyPatch, case_id: str) -> None:
    case = _case_by_id(case_id)
    monkeypatch.setattr(
        ai_search_service,
        "complete",
        lambda *args, **kwargs: json.dumps(case["llm_response"], ensure_ascii=False),
    )

    interpreted = ai_search_service._interpret_needs(case["query"], _filters_from_case(case))

    assert [need.model_dump() for need in interpreted.needs] == case["expected_needs"]
    assert interpreted.unresolved == case["expected_unresolved"]


@pytest.mark.parametrize(
    "case_id",
    [
        "one_room_two_living_three_person_family",
        "two_room_one_living_three_person_family",
        "three_room_two_living_four_person_family",
        "pure_filters_only",
        "elderly_quiet_unresolved",
    ],
)
def test_detect_tensions_cases(case_id: str) -> None:
    case = _case_by_id(case_id)

    notices = ai_search_service._detect_tensions(_needs_from_case(case), _filters_from_case(case))

    assert [notice.model_dump() for notice in notices] == case["expected_notices"]


def test_ai_search_surfaces_interpreted_intent_and_tension_notice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _case_by_id("one_room_two_living_three_person_family")
    interpreted_needs = InterpretedNeeds(
        needs=_needs_from_case(case),
        unresolved=case["expected_unresolved"],
    )
    _stub_ai_search_dependencies(monkeypatch, _filters_from_case(case), interpreted_needs)

    result = ai_search_service.ai_search(case["query"], page=1, page_size=20)

    assert [intent.model_dump() for intent in result.interpreted_intent] == case["expected_interpreted_intent"]
    assert [need.model_dump() for need in result.interpreted_needs.needs] == case["expected_needs"]
    assert [notice.model_dump() for notice in result.interpreted_needs.notices] == case["expected_notices"]
    assert result.interpreted_needs.unresolved == case["expected_unresolved"]


def test_ai_search_preserves_unresolved_needs(monkeypatch: pytest.MonkeyPatch) -> None:
    case = _case_by_id("elderly_quiet_unresolved")
    interpreted_needs = InterpretedNeeds(
        needs=_needs_from_case(case),
        unresolved=case["expected_unresolved"],
    )
    _stub_ai_search_dependencies(monkeypatch, _filters_from_case(case), interpreted_needs)

    result = ai_search_service.ai_search(case["query"], page=1, page_size=20)

    assert [need.model_dump() for need in result.interpreted_needs.needs] == case["expected_needs"]
    assert result.interpreted_needs.unresolved == case["expected_unresolved"]
    assert [notice.model_dump() for notice in result.interpreted_needs.notices] == case["expected_notices"]


def test_ai_search_non_search_query_returns_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    case = _case_by_id("non_search_query")
    monkeypatch.setattr(
        ai_search_service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-key", llm_api_key="test-key"),
    )

    result = ai_search_service.ai_search(case["query"], page=1, page_size=20)

    assert result.query_parsed is False
    assert result.items == []
    assert result.ai_summary == ai_search_service._NON_SEARCH_REDIRECT_MESSAGE
    assert result.interpreted_intent == []
    assert result.interpreted_needs.model_dump() == {
        "needs": [],
        "notices": [],
        "unresolved": [],
    }


def test_interpret_needs_discards_unknown_type(monkeypatch: pytest.MonkeyPatch) -> None:
    # A18: LLM returns a need type not in the allowed enum; it must be silently dropped.
    # A valid need in the same response must still be returned normally.
    llm_response = json.dumps(
        {
            "needs": [
                {"type": "unknown_future_type", "value": "foo", "raw": "foo"},
                {"type": "household_size", "value": 3, "raw": "一家三口"},
            ],
            "unresolved": [],
        },
        ensure_ascii=False,
    )
    monkeypatch.setattr(ai_search_service, "complete", lambda *args, **kwargs: llm_response)

    from app.schemas.search import SearchFilters

    interpreted = ai_search_service._interpret_needs("一室两厅 一家三口", SearchFilters())

    assert len(interpreted.needs) == 1
    assert interpreted.needs[0].type == "household_size"
    assert interpreted.needs[0].value == 3
    assert interpreted.unresolved == []


def test_ai_search_interpret_needs_exception_returns_empty_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A19: When _interpret_needs raises, ai_search must catch the exception,
    # return an empty InterpretedNeeds, and complete the search normally.
    case = _case_by_id("one_room_two_living_three_person_family")
    empty_needs = InterpretedNeeds()

    _stub_ai_search_dependencies(monkeypatch, _filters_from_case(case), empty_needs)
    monkeypatch.setattr(
        ai_search_service,
        "_interpret_needs",
        lambda query, filters: (_ for _ in ()).throw(RuntimeError("LLM unavailable")),
    )

    result = ai_search_service.ai_search(case["query"], page=1, page_size=20)

    assert result.interpreted_needs.model_dump() == {
        "needs": [],
        "notices": [],
        "unresolved": [],
    }
    assert result.ai_summary == "summary"
