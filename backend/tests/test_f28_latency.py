from types import SimpleNamespace

import pytest

from app.schemas.ai_search import InterpretedNeeds
from app.schemas.search import SearchFilters
from app.services.ai_search import service


def _configure_ai_search_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(embedding_api_key="test-embedding-key", llm_api_key="test-llm-key"),
    )
    monkeypatch.setattr(service, "_is_property_search", lambda query: True)
    monkeypatch.setattr(service, "_parse_filters", lambda query: (SearchFilters(), False))
    monkeypatch.setattr(service, "_extract_living_rooms", lambda query: None)
    monkeypatch.setattr(service, "_build_parsed_constraints", lambda parsed_filters: [])
    monkeypatch.setattr(service, "_build_match_reasons", lambda items, parsed_filters: {})
    monkeypatch.setattr(service, "_generate_summary", lambda query, parsed_filters, total, items, relaxed_conditions: "summary")


def test_ai_search_submits_interpret_and_resolve_before_waiting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configure_ai_search_defaults(monkeypatch)

    events: list[str] = []

    monkeypatch.setattr(service, "_interpret_needs", lambda query, parsed_filters: InterpretedNeeds())
    monkeypatch.setattr(
        service,
        "_resolve_result_ids",
        lambda query, parsed_filters, query_parsed: ["prop-1"],
    )
    monkeypatch.setattr(service, "_collect_items", lambda result_ids, page, page_size: ([], 0))

    class FakeFuture:
        def __init__(self, label: str, fn, args: tuple[object, ...], kwargs: dict[str, object]) -> None:
            self.label = label
            self.fn = fn
            self.args = args
            self.kwargs = kwargs

        def result(self):
            events.append(f"result:{self.label}")
            return self.fn(*self.args, **self.kwargs)

    class FakeExecutor:
        def __init__(self, *, max_workers: int) -> None:
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def submit(self, fn, *args, **kwargs):
            events.append(f"submit:{fn.__name__}")
            return FakeFuture(fn.__name__, fn, args, kwargs)

    monkeypatch.setattr(service, "ThreadPoolExecutor", FakeExecutor)

    result = service.ai_search("2 bedroom condo", page=1, page_size=20)

    assert result.total == 0
    assert events[:3] == [
        "submit:_run_interpret_needs",
        "submit:_run_resolve_result_ids",
        "result:_run_interpret_needs",
    ]
    assert events[3] == "result:_run_resolve_result_ids"


def test_ai_search_uses_resolved_ids_when_interpretation_fails(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _configure_ai_search_defaults(monkeypatch)

    collected_result_ids: list[str] = []

    def _collect_items(result_ids: list[str], page: int, page_size: int):
        collected_result_ids.extend(result_ids)
        return [], len(result_ids)

    monkeypatch.setattr(
        service,
        "_interpret_needs",
        lambda query, parsed_filters: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        service,
        "_resolve_result_ids",
        lambda query, parsed_filters, query_parsed: ["prop-123"],
    )
    monkeypatch.setattr(service, "_collect_items", _collect_items)

    result = service.ai_search("2 bedroom condo", page=1, page_size=20)

    assert collected_result_ids == ["prop-123"]
    assert result.interpreted_needs == InterpretedNeeds()
    assert result.total == 1
    assert any(record.message == "Need interpretation failed" for record in caplog.records)
