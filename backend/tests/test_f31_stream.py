from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.schemas.ai_search import (
    AiSearchParsingEventData,
    AiSearchSearchingEventData,
    AiSearchSummarizingEventData,
    ConstraintInfo,
    MatchReason,
    RelaxationRecord,
)
from app.schemas.property import Property, PropertyStatus
from app.schemas.search import SearchFilters
from app.services.ai_search import service


def _property(property_id: str, title: str) -> Property:
    return Property(
        id=property_id,
        title=title,
        description=f"{title} description",
        price=1000000.0,
        location="Seattle, WA",
        bedrooms=2,
        bathrooms=2,
        area_sqm=90.0,
        built_year=2020,
        subway_distance_m=400,
        images=[],
        status=PropertyStatus.AVAILABLE,
        created_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
    )


class FakeFuture:
    def __init__(self, label: str, fn, args: tuple[object, ...], kwargs: dict[str, object], call_order: list[str]) -> None:
        self.label = label
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.call_order = call_order

    def result(self):
        self.call_order.append(f"result:{self.label}")
        return self.fn(*self.args, **self.kwargs)


class FakeExecutor:
    def __init__(self, *, max_workers: int, call_order: list[str]) -> None:
        self.max_workers = max_workers
        self.call_order = call_order

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def submit(self, fn, *args, **kwargs):
        self.call_order.append(f"submit:{fn.__name__}")
        return FakeFuture(fn.__name__, fn, args, kwargs, self.call_order)


def _configure_stream_defaults(
    monkeypatch: pytest.MonkeyPatch,
    *,
    call_order: list[str] | None = None,
    parse_filters_hook=None,
    resolve_result_ids_hook=None,
    generate_summary_hook=None,
    interpret_needs_hook=None,
) -> None:
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-embedding-key", llm_api_key="test-llm-key"),
    )
    monkeypatch.setattr(service, "_is_property_search", lambda query: True)

    parsed_filters = SearchFilters(location="Seattle")
    parsed_constraints = [
        ConstraintInfo(field="location", value="Seattle", strength="soft", label="区域：Seattle")
    ]
    strict_item = _property("prop-1", "Strict Match")
    recommended_item = _property("prop-2", "Recommended Match")
    relaxations = [RelaxationRecord(field="location", from_value="Seattle", to_value=None)]
    match_reasons = {
        "prop-1": [MatchReason(field="location", label="区域：Seattle", matched=True, strength="soft")],
        "prop-2": [MatchReason(field="location", label="区域：Seattle", matched=False, strength="soft")],
    }

    if parse_filters_hook is None:
        def parse_filters_hook(query: str):
            if call_order is not None:
                call_order.append("call:_parse_filters")
            return parsed_filters, True

    if resolve_result_ids_hook is None:
        def resolve_result_ids_hook(query: str, filters: SearchFilters, **kwargs):
            if call_order is not None:
                call_order.append("call:_resolve_result_ids")
            assert kwargs["query_embedding"] == "embedding"
            assert kwargs["semantic_ids"] == ["prop-1", "prop-2"]
            assert kwargs["semantic_search_failed"] is False
            return ["prop-1", "prop-2"], kwargs["query_embedding"], kwargs["semantic_ids"], False

    if generate_summary_hook is None:
        def generate_summary_hook(
            query: str,
            filters: SearchFilters,
            total: int,
            items: list[Property],
            relaxed_conditions: list[str],
        ) -> str:
            if call_order is not None:
                call_order.append("call:_generate_summary")
            return "Two matches found."

    monkeypatch.setattr(service, "_parse_filters", parse_filters_hook)
    monkeypatch.setattr(service, "_build_parsed_constraints", lambda filters: parsed_constraints)
    monkeypatch.setattr(service, "_run_semantic_prefetch", lambda query: ("embedding", ["prop-1", "prop-2"], False))
    monkeypatch.setattr(service, "_resolve_result_ids", resolve_result_ids_hook)
    monkeypatch.setattr(
        service,
        "_filter_ranked_result_ids",
        lambda property_ids, filters, **kwargs: ["prop-1"] if not kwargs.get("exclude_ids") else ["prop-2"],
    )
    monkeypatch.setattr(
        service,
        "_apply_relaxation",
        lambda query, filters, query_parsed, **kwargs: (["prop-1", "prop-2"], SearchFilters(), [], 1),
    )
    monkeypatch.setattr(service, "_build_relaxations", lambda original, relaxed: relaxations)
    monkeypatch.setattr(service, "_build_relaxation_summary", lambda strict_ids, recommended_ids, records: ["Relaxed location"])
    monkeypatch.setattr(service, "_collect_items", lambda result_ids, page, page_size: ([strict_item, recommended_item], 2))
    monkeypatch.setattr(service, "_build_match_reasons", lambda items, filters: match_reasons)
    monkeypatch.setattr(service, "_generate_summary", generate_summary_hook)
    monkeypatch.setattr(
        service,
        "_interpret_needs",
        interpret_needs_hook or (lambda query, filters: (_ for _ in ()).throw(AssertionError("_interpret_needs should not run"))),
    )
    monkeypatch.setattr(
        service,
        "ThreadPoolExecutor",
        lambda *, max_workers: FakeExecutor(max_workers=max_workers, call_order=call_order or []),
    )


def test_ai_search_stream_emits_f31_event_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    call_order: list[str] = []
    _configure_stream_defaults(monkeypatch, call_order=call_order)

    stream_events = list(service.ai_search_stream("quiet Seattle condo", page=1, page_size=20))

    assert [event for event, _ in stream_events] == [
        "started",
        "parsing",
        "parsed",
        "searching",
        "results",
        "summarizing",
        "summary",
        "done",
    ]
    assert stream_events[1][1].model_dump() == AiSearchParsingEventData().model_dump()
    assert stream_events[3][1].model_dump() == AiSearchSearchingEventData(message="检索匹配房源中...").model_dump()
    assert stream_events[5][1].model_dump() == AiSearchSummarizingEventData().model_dump()


def test_ai_search_stream_emits_parsing_before_parse_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    call_order: list[str] = []
    _configure_stream_defaults(monkeypatch, call_order=call_order)

    stream = service.ai_search_stream("quiet Seattle condo", page=1, page_size=20)

    assert next(stream)[0] == "started"
    parsing_event, parsing_data = next(stream)

    assert parsing_event == "parsing"
    assert parsing_data.model_dump() == AiSearchParsingEventData().model_dump()
    assert "call:_parse_filters" not in call_order

    stream.close()


def test_ai_search_stream_emits_summarizing_before_generate_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    call_order: list[str] = []
    _configure_stream_defaults(monkeypatch, call_order=call_order)

    stream = service.ai_search_stream("quiet Seattle condo", page=1, page_size=20)

    assert next(stream)[0] == "started"
    assert next(stream)[0] == "parsing"
    assert next(stream)[0] == "parsed"
    assert next(stream)[0] == "searching"
    assert next(stream)[0] == "results"

    summarizing_event, summarizing_data = next(stream)

    assert summarizing_event == "summarizing"
    assert summarizing_data.model_dump() == AiSearchSummarizingEventData().model_dump()
    assert "call:_generate_summary" not in call_order

    summary_event, _ = next(stream)
    assert summary_event == "summary"
    assert "call:_generate_summary" in call_order


def test_ai_search_stream_emits_results_without_interpret_needs(monkeypatch: pytest.MonkeyPatch) -> None:
    call_order: list[str] = []
    _configure_stream_defaults(monkeypatch, call_order=call_order)

    stream = service.ai_search_stream("quiet Seattle condo", page=1, page_size=20)
    events = [next(stream)[0] for _ in range(5)]

    assert events == ["started", "parsing", "parsed", "searching", "results"]
    assert all("_interpret_needs" not in entry for entry in call_order)
