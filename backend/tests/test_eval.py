import json
from pathlib import Path

from app.services.ai_search.service import _normalize_query


EVAL_SET_PATH = Path(__file__).with_name("eval_set.json")


def _load_eval_set() -> list[dict[str, object]]:
    return json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))


def test_eval_set_has_minimum_coverage() -> None:
    assert len(_load_eval_set()) >= 25


def test_normalize_query_meets_eval_threshold() -> None:
    eval_set = _load_eval_set()
    passing_queries = 0
    failures: list[str] = []

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
            continue

        passing_queries += 1

    pass_ratio = passing_queries / len(eval_set)
    assert pass_ratio >= 0.8, (
        f"pass ratio {pass_ratio:.2%} below 80%; failures: {failures}"
    )
