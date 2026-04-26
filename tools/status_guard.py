#!/usr/bin/env python3
"""Guard and transition feature status.json files.

This tool is intentionally orchestration-owned. Workers must not call it.
Claude Code may call it before/after worker execution to keep state transitions
small, atomic, and machine-checkable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any
import fnmatch


VALID_TASK_STATUSES = {"pending", "in_progress", "done", "failed", "blocked"}
VALID_FEATURE_STATUSES = {"pending", "in_progress", "done", "failed", "blocked"}


class GuardError(Exception):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_status(feature_dir: Path) -> dict[str, Any]:
    status_file = feature_dir / "status.json"
    if not status_file.is_file():
        raise GuardError(f"missing status.json: {status_file}")
    try:
        return json.loads(status_file.read_text())
    except json.JSONDecodeError as exc:
        raise GuardError(f"invalid JSON in {status_file}: {exc}") from exc


def write_status_atomic(feature_dir: Path, data: dict[str, Any]) -> None:
    status_file = feature_dir / "status.json"
    fd, tmp_name = tempfile.mkstemp(prefix="status.", suffix=".json", dir=str(feature_dir))
    try:
        with os.fdopen(fd, "w") as tmp:
            json.dump(data, tmp, indent=2)
            tmp.write("\n")
        os.replace(tmp_name, status_file)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def find_task(data: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in data.get("tasks", []):
        if task.get("id") == task_id:
            return task
    raise GuardError(f"task not found in status.json: {task_id}")


def expected_artifact(task: dict[str, Any]) -> str:
    owner = task.get("owner")
    task_type = task.get("type")
    task_id = task.get("id")
    if task_type == "review":
        return "review.md"
    if task_type == "acceptance" or owner == "claude":
        return "final-report.md"
    if owner == "codex":
        return f"codex-build-{task_id}.md"
    if owner == "gemini":
        return f"gemini-build-{task_id}.md"
    raise GuardError(f"cannot infer artifact for task {task_id}: owner={owner!r}, type={task_type!r}")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_manifest(feature_dir: Path) -> dict[str, Any] | None:
    manifest_file = feature_dir / "task_manifest.json"
    if not manifest_file.is_file():
        return None
    try:
        return json.loads(manifest_file.read_text())
    except json.JSONDecodeError as exc:
        raise GuardError(f"invalid JSON in {manifest_file}: {exc}") from exc


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def collect_changed_files() -> set[str]:
    import subprocess

    def lines(cmd: list[str]) -> list[str]:
        out = subprocess.check_output(cmd, text=True)
        return [line for line in out.splitlines() if line]

    changed = set(lines(["git", "diff", "--name-only"]))
    changed.update(lines(["git", "diff", "--name-only", "--cached"]))
    changed.update(lines(["git", "ls-files", "--others", "--exclude-standard"]))
    return changed


def append_log(data: dict[str, Any], event: str, by: str = "claude") -> None:
    data.setdefault("activity_log", []).append(
        {
            "timestamp": utc_now(),
            "event": event,
            "by": by,
        }
    )


def dependency_errors(data: dict[str, Any], task: dict[str, Any], require_done: bool = True) -> list[str]:
    errors: list[str] = []
    tasks = {t.get("id"): t for t in data.get("tasks", [])}
    for dep_id in task.get("depends_on", []):
        dep = tasks.get(dep_id)
        if dep is None:
            errors.append(f"{task['id']} depends on missing task {dep_id}")
        elif require_done and dep.get("status") != "done":
            errors.append(f"{task['id']} depends on {dep_id}, but {dep_id} is {dep.get('status')}")
    return errors


def first_runnable_task(data: dict[str, Any]) -> dict[str, Any] | None:
    for task in data.get("tasks", []):
        if task.get("status") == "pending" and not dependency_errors(data, task):
            return task
    return None


def validate_status(feature_dir: Path) -> tuple[list[str], list[str]]:
    data = load_status(feature_dir)
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("status") not in VALID_FEATURE_STATUSES:
        errors.append(f"feature status is invalid: {data.get('status')!r}")

    task_ids: set[str] = set()
    in_progress = []
    for task in data.get("tasks", []):
        task_id = task.get("id")
        if not task_id:
            errors.append("task without id")
            continue
        if task_id in task_ids:
            errors.append(f"duplicate task id: {task_id}")
        task_ids.add(task_id)

        status = task.get("status")
        if status not in VALID_TASK_STATUSES:
            errors.append(f"{task_id} has invalid status: {status!r}")
        if status == "in_progress":
            in_progress.append(task_id)

        owner = task.get("owner")
        task_type = task.get("type")
        if owner not in {"codex", "gemini", "claude"}:
            errors.append(f"{task_id} has unsupported owner: {owner!r}")
        if task_type == "review" and owner != "codex":
            errors.append(f"{task_id} is type=review but owner is {owner!r}")
        if task_type == "acceptance" and owner != "claude":
            errors.append(f"{task_id} is type=acceptance but owner is {owner!r}")

        for dep_error in dependency_errors(data, task, require_done=False):
            errors.append(dep_error)
        if status in {"in_progress", "done"}:
            for dep_error in dependency_errors(data, task, require_done=True):
                errors.append(dep_error)

        artifact = task.get("artifact")
        if status == "done":
            try:
                expected = expected_artifact(task)
            except GuardError as exc:
                errors.append(str(exc))
                continue
            if artifact != expected:
                errors.append(f"{task_id} artifact should be {expected!r}, got {artifact!r}")
            elif not (feature_dir / expected).is_file():
                errors.append(f"{task_id} is done but artifact is missing: {expected}")
        elif artifact:
            warnings.append(f"{task_id} is {status} but still records artifact {artifact!r}")

    if len(in_progress) > 1:
        errors.append(f"multiple tasks are in_progress: {', '.join(in_progress)}")

    current_owner = data.get("current_owner")
    current_stage = data.get("current_stage")
    if current_owner is not None and current_owner not in {"codex", "gemini", "claude"}:
        errors.append(f"current_owner is invalid: {current_owner!r}")
    if current_stage and current_stage.endswith("_running"):
        running_id = current_stage.removesuffix("_running")
        try:
            running_task = find_task(data, running_id)
        except GuardError:
            errors.append(f"current_stage points at missing task: {current_stage}")
        else:
            if running_task.get("status") != "in_progress":
                errors.append(f"current_stage is {current_stage}, but {running_id} is {running_task.get('status')}")
            if current_owner != running_task.get("owner"):
                errors.append(f"current_owner should be {running_task.get('owner')!r}, got {current_owner!r}")

    if data.get("status") == "done":
        final_report = feature_dir / "final-report.md"
        if not final_report.is_file():
            errors.append("feature is done but final-report.md is missing")
        else:
            text = final_report.read_text(errors="replace").lower()
            if "accepted" not in text:
                errors.append("feature is done but final-report.md does not contain an accepted disposition")

    return errors, warnings


def validate_artifact(feature_dir: Path, task_id: str) -> None:
    data = load_status(feature_dir)
    task = find_task(data, task_id)
    artifact = expected_artifact(task)
    path = feature_dir / artifact
    if not path.is_file():
        raise GuardError(f"expected artifact was not created: {artifact}")
    text = path.read_text(errors="replace")
    nonempty = [line.strip() for line in text.splitlines() if line.strip()]
    first = nonempty[0] if nonempty else ""

    if task.get("type") == "review":
        required = ["# Review", "## Verdict", "## Criteria Results", "## Issues Found", "## Required Fixes"]
        if first != "# Review":
            raise GuardError(f"{artifact} must start with '# Review'")
    elif task.get("owner") == "codex":
        required = ["# Codex Build Report", "## Task Completed", "## Files Changed", "## Open Issues"]
        if first != "# Codex Build Report":
            raise GuardError(f"{artifact} must start with '# Codex Build Report'")
        if f"- {task_id}" not in text:
            raise GuardError(f"{artifact} must list the completed task as '- {task_id}'")
    elif task.get("owner") == "gemini":
        required = ["# Gemini Build Report", "## Task Completed", "## Open Issues"]
        if first != "# Gemini Build Report":
            raise GuardError(f"{artifact} must start with '# Gemini Build Report'")
        if f"- {task_id}" not in text:
            raise GuardError(f"{artifact} must list the completed task as '- {task_id}'")
    else:
        return

    missing = [section for section in required if section not in text]
    if missing:
        raise GuardError(f"{artifact} is missing required section(s): {', '.join(missing)}")


def require_preflight(feature_dir: Path, task_id: str) -> None:
    errors, warnings = validate_status(feature_dir)
    blocking_errors = [e for e in errors if not e.startswith(f"{task_id} is done")]
    if blocking_errors:
        raise GuardError("status.json invariant check failed:\n- " + "\n- ".join(blocking_errors))
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    data = load_status(feature_dir)
    task = find_task(data, task_id)
    status = task.get("status")
    if status not in {"pending", "in_progress"}:
        raise GuardError(f"task {task_id} status is {status!r}; expected pending or in_progress")
    if task.get("owner") == "claude" or task.get("type") == "acceptance":
        raise GuardError(f"task {task_id} is Claude-owned acceptance; run it manually in Claude Code")
    if task.get("owner") not in {"codex", "gemini"}:
        raise GuardError(f"task {task_id} has unsupported executable owner: {task.get('owner')!r}")

    dep_errors = dependency_errors(data, task)
    if dep_errors:
        raise GuardError("dependency check failed:\n- " + "\n- ".join(dep_errors))

    artifact = feature_dir / expected_artifact(task)
    if artifact.exists() and os.environ.get("ALLOW_ARTIFACT_OVERWRITE") != "true":
        raise GuardError(
            f"target artifact already exists: {artifact}. "
            "Set ALLOW_ARTIFACT_OVERWRITE=true only for an intentional retry."
        )

    manifest = load_manifest(feature_dir)
    if manifest:
        manifest_task = manifest.get("tasks", {}).get(task_id)
        if not manifest_task:
            raise GuardError(f"task_manifest.json is missing task {task_id}")
        manifest_artifact = manifest_task.get("expected_artifact")
        expected = expected_artifact(task)
        if manifest_artifact and manifest_artifact != expected:
            raise GuardError(
                f"task_manifest.json expected_artifact for {task_id} is "
                f"{manifest_artifact!r}, but status expects {expected!r}"
            )


def check_scope(feature_dir: Path, task_id: str, baseline_file: Path) -> None:
    manifest = load_manifest(feature_dir)
    if not manifest:
        print("scope check skipped: no task_manifest.json")
        return

    data = load_status(feature_dir)
    task = find_task(data, task_id)
    manifest_task = manifest.get("tasks", {}).get(task_id)
    if not manifest_task:
        raise GuardError(f"task_manifest.json is missing task {task_id}")

    before = {line.strip() for line in baseline_file.read_text().splitlines() if line.strip()}
    after = collect_changed_files()
    changed = sorted(after - before)
    if not changed:
        print("scope check passed: no new changed paths")
        return

    expected = repo_relative(feature_dir / expected_artifact(task))
    allowed = list(manifest_task.get("allowed_files", []))
    if expected not in allowed:
        allowed.append(expected)
    forbidden = list(manifest_task.get("forbidden_files", []))

    forbidden_hits = [path for path in changed if matches_any(path, forbidden)]
    if forbidden_hits:
        raise GuardError("scope check failed; forbidden path(s) changed:\n- " + "\n- ".join(forbidden_hits))

    if allowed:
        outside = [path for path in changed if not matches_any(path, allowed)]
        if outside:
            raise GuardError("scope check failed; path(s) outside allowed_files:\n- " + "\n- ".join(outside))

    print("scope check passed")


def transition_start(feature_dir: Path, task_id: str) -> None:
    data = load_status(feature_dir)
    task = find_task(data, task_id)
    status = task.get("status")
    if status not in {"pending", "in_progress"}:
        raise GuardError(f"{task_id} is {status!r}; only pending or in_progress tasks can be started")
    dep_errors = dependency_errors(data, task)
    if dep_errors:
        raise GuardError("dependency check failed:\n- " + "\n- ".join(dep_errors))
    task["status"] = "in_progress"
    data["status"] = "in_progress"
    data["current_stage"] = f"{task_id}_running"
    data["current_owner"] = task.get("owner")
    data["next_step"] = f"Wait for {task_id} artifact"
    append_log(data, f"{task_id} started — {task.get('title', 'task')}") 
    write_status_atomic(feature_dir, data)


def transition_done(feature_dir: Path, task_id: str) -> None:
    data = load_status(feature_dir)
    task = find_task(data, task_id)
    artifact = expected_artifact(task)
    task["status"] = "done"
    task["artifact"] = artifact
    data["current_stage"] = f"{task_id}_done"
    data["current_owner"] = None

    if task.get("type") == "acceptance" or task.get("owner") == "claude":
        final_report = (feature_dir / artifact).read_text(errors="replace").lower()
        disposition_lines = [line for line in final_report.splitlines() if "disposition" in line]
        disposition_text = "\n".join(disposition_lines) if disposition_lines else final_report
        if "accepted" in disposition_text and "failed" not in disposition_text:
            data["status"] = "done"
            data["next_step"] = f"{data.get('feature', 'feature')} complete"
        else:
            data["status"] = "failed"
            data["next_step"] = "Inspect final-report.md and requeue failed task(s)"
        append_log(data, f"{task_id} done — final acceptance artifact captured as {artifact}")
        write_status_atomic(feature_dir, data)
        return

    next_task = first_runnable_task(data)
    if next_task:
        data["next_step"] = f"Start {next_task['id']} — {next_task.get('title', 'next task')}"
    else:
        pending = [t for t in data.get("tasks", []) if t.get("status") == "pending"]
        if pending:
            data["next_step"] = "Resolve blocked task dependencies"
            data["status"] = "blocked"
        else:
            data["next_step"] = "All worker tasks complete; Claude acceptance may be required"

    append_log(data, f"{task_id} done — artifact captured as {artifact}")
    write_status_atomic(feature_dir, data)


def transition_fail(feature_dir: Path, task_id: str, reason: str) -> None:
    data = load_status(feature_dir)
    task = find_task(data, task_id)
    task["status"] = "failed"
    data["status"] = "failed"
    data["current_stage"] = f"{task_id}_failed"
    data["current_owner"] = None
    data["next_step"] = f"Inspect {task_id} failure, then requeue to pending if retrying"
    append_log(data, f"{task_id} failed — {reason}")
    write_status_atomic(feature_dir, data)


def transition_requeue(feature_dir: Path, task_id: str, reason: str) -> None:
    data = load_status(feature_dir)
    task = find_task(data, task_id)
    if task.get("status") not in {"failed", "blocked", "in_progress"}:
        raise GuardError(f"{task_id} is {task.get('status')!r}; only failed, blocked, or in_progress tasks can be requeued")
    task["status"] = "pending"
    task["artifact"] = None
    data["status"] = "in_progress"
    data["current_stage"] = f"{task_id}_pending"
    data["current_owner"] = None
    data["next_step"] = f"Retry {task_id} — {task.get('title', 'task')}"
    append_log(data, f"{task_id} requeued — {reason}")
    write_status_atomic(feature_dir, data)


def cmd_validate(args: argparse.Namespace) -> int:
    errors, warnings = validate_status(Path(args.feature_dir))
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print("status.json invariant check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("status.json invariant check passed")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    data = load_status(Path(args.feature_dir))
    task = first_runnable_task(data)
    if not task:
        print("")
        return 1
    print(task["id"])
    return 0


def cmd_task_info(args: argparse.Namespace) -> int:
    data = load_status(Path(args.feature_dir))
    task = find_task(data, args.task_id)
    print(f"{task.get('owner')} {task.get('type')} {task.get('status')} {expected_artifact(task)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and transition feature status.json")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ["validate", "next"]:
        p = sub.add_parser(name)
        p.add_argument("feature_dir")

    p = sub.add_parser("task-info")
    p.add_argument("feature_dir")
    p.add_argument("task_id")

    p = sub.add_parser("preflight")
    p.add_argument("feature_dir")
    p.add_argument("task_id")

    p = sub.add_parser("validate-artifact")
    p.add_argument("feature_dir")
    p.add_argument("task_id")

    p = sub.add_parser("check-scope")
    p.add_argument("feature_dir")
    p.add_argument("task_id")
    p.add_argument("baseline_file")

    p = sub.add_parser("start")
    p.add_argument("feature_dir")
    p.add_argument("task_id")

    p = sub.add_parser("done")
    p.add_argument("feature_dir")
    p.add_argument("task_id")

    p = sub.add_parser("fail")
    p.add_argument("feature_dir")
    p.add_argument("task_id")
    p.add_argument("reason", nargs="?", default="worker command failed")

    p = sub.add_parser("requeue")
    p.add_argument("feature_dir")
    p.add_argument("task_id")
    p.add_argument("reason", nargs="?", default="retry approved by Claude")

    args = parser.parse_args()
    feature_dir = Path(getattr(args, "feature_dir", ".")).resolve()

    try:
        if args.command == "validate":
            return cmd_validate(args)
        if args.command == "next":
            return cmd_next(args)
        if args.command == "task-info":
            return cmd_task_info(args)
        if args.command == "preflight":
            require_preflight(feature_dir, args.task_id)
            print("preflight passed")
        elif args.command == "validate-artifact":
            validate_artifact(feature_dir, args.task_id)
            print("artifact check passed")
        elif args.command == "check-scope":
            check_scope(feature_dir, args.task_id, Path(args.baseline_file))
        elif args.command == "start":
            transition_start(feature_dir, args.task_id)
            print(f"{args.task_id} marked in_progress")
        elif args.command == "done":
            validate_artifact(feature_dir, args.task_id)
            transition_done(feature_dir, args.task_id)
            print(f"{args.task_id} marked done")
        elif args.command == "fail":
            transition_fail(feature_dir, args.task_id, args.reason)
            print(f"{args.task_id} marked failed")
        elif args.command == "requeue":
            transition_requeue(feature_dir, args.task_id, args.reason)
            print(f"{args.task_id} requeued")
        return 0
    except GuardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
