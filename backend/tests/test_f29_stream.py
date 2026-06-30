import importlib
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# __init__.py shadows the `router` attribute with the APIRouter instance;
# importlib bypasses attribute lookup and returns the actual module object.
ai_search_router_module = importlib.import_module("app.api.v1.ai_search.router")
from app.core.security import get_current_user
from app.schemas.ai_search import (
    AiSearchSearchingEventData,
    AiSearchStreamEmpty,
    ConstraintInfo,
    InterpretedNeeds,
    MatchReason,
    RelaxationRecord,
    SearchNotice,
    UserNeed,
)
from app.schemas.auth import UserRead
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


def test_ai_search_stream_emits_events_in_causal_order_and_expected_payloads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-embedding-key", llm_api_key="test-llm-key"),
    )

    call_order: list[str] = []
    parsed_filters = SearchFilters(location="Seattle")
    parsed_constraints = [
        ConstraintInfo(field="location", value="Seattle", strength="soft", label="区域：Seattle")
    ]
    interpreted_needs = InterpretedNeeds(
        needs=[UserNeed(type="quiet_environment", value=True, raw="quiet")],
        unresolved=["close to school"],
    )
    notices = [SearchNotice(type="suggestion", message="Quiet areas may be farther out.")]
    relaxations = [RelaxationRecord(field="location", from_value="Seattle", to_value=None)]
    strict_item = _property("prop-1", "Strict Match")
    recommended_item = _property("prop-2", "Recommended Match")
    match_reasons = {
        "prop-1": [MatchReason(field="location", label="区域：Seattle", matched=True, strength="soft")],
        "prop-2": [MatchReason(field="location", label="区域：Seattle", matched=False, strength="soft")],
    }

    monkeypatch.setattr(service, "_is_property_search", lambda query: True)

    def _parse_filters(query: str):
        call_order.append("call:_parse_filters")
        return parsed_filters, True

    def _interpret_needs(query: str, filters: SearchFilters):
        call_order.append("call:_interpret_needs")
        return interpreted_needs

    def _resolve_result_ids(query: str, filters: SearchFilters, **kwargs):
        call_order.append("call:_resolve_result_ids")
        return ["prop-1", "prop-2"], None, [], False

    def _filter_ranked_result_ids(property_ids: list[str], filters: SearchFilters, **kwargs):
        call_order.append("call:_filter_ranked_result_ids")
        if kwargs.get("exclude_ids"):
            return ["prop-2"]
        return ["prop-1"]

    def _apply_relaxation(query: str, filters: SearchFilters, query_parsed: bool, **kwargs):
        call_order.append("call:_apply_relaxation")
        return ["prop-1", "prop-2"], SearchFilters(), ["Removed the location filter."], 1

    def _collect_items(result_ids: list[str], page: int, page_size: int):
        call_order.append("call:_collect_items")
        assert result_ids == ["prop-1", "prop-2"]
        return [strict_item, recommended_item], 2

    def _generate_summary(
        query: str,
        filters: SearchFilters,
        total: int,
        items: list[Property],
        relaxed_conditions: list[str],
    ) -> str:
        call_order.append("call:_generate_summary")
        assert [item.id for item in items] == ["prop-1", "prop-2"]
        assert relaxed_conditions == ["Relaxed location"]
        return "Two matches found."

    class FakeFuture:
        def __init__(self, label: str, fn, args: tuple[object, ...], kwargs: dict[str, object]) -> None:
            self.label = label
            self.fn = fn
            self.args = args
            self.kwargs = kwargs

        def result(self):
            call_order.append(f"result:{self.label}")
            return self.fn(*self.args, **self.kwargs)

    class FakeExecutor:
        def __init__(self, *, max_workers: int) -> None:
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def submit(self, fn, *args, **kwargs):
            call_order.append(f"submit:{fn.__name__}")
            return FakeFuture(fn.__name__, fn, args, kwargs)

    monkeypatch.setattr(service, "_parse_filters", _parse_filters)
    monkeypatch.setattr(service, "_build_parsed_constraints", lambda filters: parsed_constraints)
    monkeypatch.setattr(service, "_interpret_needs", _interpret_needs)
    monkeypatch.setattr(service, "_detect_tensions", lambda needs, filters: notices)
    monkeypatch.setattr(service, "_resolve_result_ids", _resolve_result_ids)
    monkeypatch.setattr(service, "_filter_ranked_result_ids", _filter_ranked_result_ids)
    monkeypatch.setattr(service, "_apply_relaxation", _apply_relaxation)
    monkeypatch.setattr(service, "_build_relaxations", lambda original, relaxed: relaxations)
    monkeypatch.setattr(service, "_build_relaxation_summary", lambda strict_ids, recommended_ids, records: ["Relaxed location"])
    monkeypatch.setattr(service, "_collect_items", _collect_items)
    monkeypatch.setattr(service, "_build_match_reasons", lambda items, filters: match_reasons)
    monkeypatch.setattr(service, "_generate_summary", _generate_summary)
    monkeypatch.setattr(service, "ThreadPoolExecutor", FakeExecutor)

    stream_events = []
    for event, data in service.ai_search_stream("quiet Seattle condo", page=1, page_size=20):
        call_order.append(f"yield:{event}")
        stream_events.append((event, data))

    assert [event for event, _ in stream_events] == [
        "started",
        "parsed",
        "searching",
        "results",
        "summary",
        "done",
    ]
    assert call_order.index("call:_parse_filters") < call_order.index("yield:parsed")
    assert call_order.index("yield:parsed") < call_order.index("submit:_run_resolve_result_ids")
    assert call_order.index("yield:parsed") < call_order.index("call:_collect_items")
    assert call_order.index("yield:results") < call_order.index("call:_generate_summary")

    parsed_event = stream_events[1][1]
    assert parsed_event.model_dump() == {
        "query_parsed": True,
        "parsed_filters": parsed_filters.model_dump(),
        "parsed_constraints": [constraint.model_dump() for constraint in parsed_constraints],
        "interpreted_intent": [],
        "interpreted_needs": InterpretedNeeds().model_dump(),
    }

    searching_event = stream_events[2][1]
    assert isinstance(searching_event, AiSearchSearchingEventData)
    assert searching_event.model_dump() == {
        "stage": "searching",
        "message": "Searching properties...",
    }

    results_event = stream_events[3][1]
    assert results_event.model_dump() == {
        "items": [strict_item.model_dump(), recommended_item.model_dump()],
        "strict_items": [strict_item.model_dump()],
        "recommended_items": [recommended_item.model_dump()],
        "total": 2,
        "page": 1,
        "page_size": 20,
        "relaxations": [relaxation.model_dump() for relaxation in relaxations],
        "match_reasons": {
            property_id: [reason.model_dump() for reason in reasons]
            for property_id, reasons in match_reasons.items()
        },
    }

    summary_event = stream_events[4][1]
    assert summary_event.model_dump() == {"ai_summary": "Two matches found."}


def test_ai_search_stream_emits_error_event_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-embedding-key", llm_api_key="test-llm-key"),
    )
    monkeypatch.setattr(service, "_is_property_search", lambda query: True)
    monkeypatch.setattr(service, "_parse_filters", lambda query: (SearchFilters(), True))
    monkeypatch.setattr(service, "_build_parsed_constraints", lambda filters: [])
    monkeypatch.setattr(service, "_interpret_needs", lambda query, filters: InterpretedNeeds())
    monkeypatch.setattr(service, "_detect_tensions", lambda needs, filters: [])
    monkeypatch.setattr(
        service,
        "_resolve_result_ids",
        lambda query, filters, **kwargs: (_ for _ in ()).throw(RuntimeError("search exploded")),
    )

    class FakeFuture:
        def __init__(self, fn, args: tuple[object, ...], kwargs: dict[str, object]) -> None:
            self.fn = fn
            self.args = args
            self.kwargs = kwargs

        def result(self):
            return self.fn(*self.args, **self.kwargs)

    class FakeExecutor:
        def __init__(self, *, max_workers: int) -> None:
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def submit(self, fn, *args, **kwargs):
            return FakeFuture(fn, args, kwargs)

    monkeypatch.setattr(service, "ThreadPoolExecutor", FakeExecutor)

    stream_events = list(service.ai_search_stream("boom", page=1, page_size=20))

    assert [event for event, _ in stream_events] == ["started", "parsed", "searching", "error"]
    assert stream_events[-1][1].model_dump() == {"message": "search exploded"}


def test_ai_search_stream_handles_non_search_query(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-embedding-key", llm_api_key="test-llm-key"),
    )
    monkeypatch.setattr(service, "_is_property_search", lambda query: False)
    monkeypatch.setattr(
        service,
        "_parse_filters",
        lambda query: (_ for _ in ()).throw(AssertionError("_parse_filters should not run")),
    )

    stream_events = list(service.ai_search_stream("why are rates rising", page=0, page_size=500))

    assert [event for event, _ in stream_events] == [
        "started",
        "parsed",
        "searching",
        "results",
        "summary",
        "done",
    ]
    assert stream_events[1][1].model_dump() == {
        "query_parsed": False,
        "parsed_filters": SearchFilters().model_dump(),
        "parsed_constraints": [],
        "interpreted_intent": [],
        "interpreted_needs": InterpretedNeeds().model_dump(),
    }
    assert stream_events[3][1].model_dump() == {
        "items": [],
        "strict_items": [],
        "recommended_items": [],
        "total": 0,
        "page": 1,
        "page_size": 100,
        "relaxations": [],
        "match_reasons": {},
    }
    assert stream_events[4][1].model_dump() == {"ai_summary": service._NON_SEARCH_REDIRECT_MESSAGE}


def test_ai_search_stream_endpoint_returns_sse_content_type(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI()
    app.include_router(ai_search_router_module.router, prefix="/api/v1/search/ai")
    app.dependency_overrides[get_current_user] = lambda: UserRead(
        id="user-123",
        email="user@example.com",
        role="user",
    )

    monkeypatch.setattr(
        ai_search_router_module,
        "ai_search_stream",
        lambda query, page, page_size: iter(
            [
                ("started", AiSearchStreamEmpty()),
                ("done", AiSearchStreamEmpty()),
            ]
        ),
    )

    with TestClient(app).stream(
        "GET",
        "/api/v1/search/ai/stream",
        params={"query": "loft"},
        headers={"Authorization": "Bearer ignored"},
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: started" in body
    assert "event: done" in body
