"""Integration tests for asynchronous sequence runs with SSE progress streaming.

Contract under test (Phase 2 streaming extension of POST /api/sequences):

1. POST /api/sequences with form field async_mode="1"
   -> HTTP 202 {"run_id": str, "stream_url": "/api/sequences/<id>/events"}.
   Without async_mode the endpoint keeps its legacy synchronous behavior.

2. GET /api/sequences/{run_id}/events -> SSE (text/event-stream):
   a sequence of `event: stage` records whose JSON data is
   {"run_id", "stage" in [queued, scene_analysis, prompt_compile, render, qc],
    "status" in [started, completed, failed], "detail": str, "progress": 0..1},
   terminated by `event: done` (data = same run JSON as the sync POST) or
   `event: error` ({"message", "code"}). Unknown run_id -> 404.
   Connecting after completion replays the terminal event immediately.

3. POST /api/sequences/{run_id}/cancel -> {"status": "cancelling"}
   (or "already_finished"); a cancelled run's stream ends with event error,
   code "cancelled". Unknown id -> 404.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import src.web.persistence as persistence
from src.web.app import app

np = pytest.importorskip("numpy")
cv2 = pytest.importorskip("cv2")

ALLOWED_STAGES = {"queued", "scene_analysis", "prompt_compile", "render", "qc"}
ALLOWED_STAGE_STATUSES = {"started", "completed", "failed"}
TERMINAL_EVENTS = {"done", "error"}

# Top-level keys of the synchronous POST /api/sequences payload, derived from an
# actual sync call against the pre-streaming handler (backward-compat baseline).
BASELINE_SYNC_RUN_KEYS = {
    "run_id",
    "created_at",
    "status",
    "intent",
    "preset",
    "params",
    "source_image",
    "analysis",
    "available_providers",
    "variants",
}

# With no provider API keys configured, a run still completes; variants land in
# a non-executed status rather than failing the request.
NO_PROVIDER_RUN_STATUSES = {"not_configured", "not_executed", "success", "failed"}


@pytest.fixture()
def isolated_web_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "animatize-web-test.db"
    if db_path.exists():
        db_path.unlink()

    monkeypatch.setattr(persistence, "DB_PATH", db_path)

    for key in [
        "RUNWAY_API_KEY",
        "PIKA_API_KEY",
        "VEO_API_KEY",
        "SORA_API_KEY",
        "OPENAI_API_KEY",
        "FLUX_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)

    persistence.init_db()
    yield


@pytest.fixture()
def client(isolated_web_env):
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sample_image_bytes() -> bytes:
    """Deterministic small JPEG the scene analyzer can consume."""
    frame = np.zeros((64, 96, 3), dtype=np.uint8)
    frame[:, :, 2] = np.tile(np.linspace(20, 220, 96, dtype=np.uint8), (64, 1))
    cv2.rectangle(frame, (30, 18), (66, 50), (200, 180, 40), thickness=-1)
    ok, encoded = cv2.imencode(".jpg", frame)
    assert ok, "cv2 failed to encode the sample test frame"
    return encoded.tobytes()


def _sequence_form(**overrides: Any) -> dict[str, str]:
    form = {
        "intent": "Slow push-in on the subject with drifting light",
        "preset": "cinematic-balanced",
        "duration": "4",
        "variants": "2",
        "aspect_ratio": "16:9",
        "motion_intensity": "5",
        "quality_mode": "balanced",
        "provider": "auto",
        "negative_intent": "",
    }
    form.update({key: str(value) for key, value in overrides.items()})
    return form


def _post_sequence(client: TestClient, **overrides: Any):
    return client.post(
        "/api/sequences",
        files={"image": ("frame.jpg", _sample_image_bytes(), "image/jpeg")},
        data=_sequence_form(**overrides),
    )


def _start_async_run(client: TestClient, **overrides: Any) -> dict[str, Any]:
    response = _post_sequence(client, async_mode="1", **overrides)
    assert response.status_code == 202, (
        f"async POST /api/sequences expected 202, got {response.status_code}: "
        f"{response.text[:500]}"
    )
    return response.json()


def _parse_sse_block(block: str) -> tuple[str, Any] | None:
    """Parse a single SSE record (lines up to a blank-line separator).

    Returns (event_name, data) where data is JSON-decoded when possible,
    or None for comment-only / empty blocks.
    """
    event_name = "message"
    data_lines: list[str] = []
    saw_field = False
    for line in block.split("\n"):
        if not line or line.startswith(":"):
            continue
        if line.startswith("event:"):
            event_name = line[len("event:"):].strip()
            saw_field = True
        elif line.startswith("data:"):
            data_lines.append(line[len("data:"):].lstrip())
            saw_field = True
    if not saw_field:
        return None
    data_raw = "\n".join(data_lines)
    if not data_raw:
        return event_name, None
    try:
        return event_name, json.loads(data_raw)
    except json.JSONDecodeError:
        return event_name, data_raw


def _collect_sse_events(
    client: TestClient,
    url: str,
    max_events: int = 200,
) -> list[tuple[str, Any]]:
    """Stream an SSE endpoint, parsing records until a terminal event or EOF."""
    events: list[tuple[str, Any]] = []
    buffer = ""
    with client.stream("GET", url) as response:
        assert response.status_code == 200, (
            f"GET {url} expected 200, got {response.status_code}"
        )
        content_type = response.headers.get("content-type", "")
        assert content_type.startswith("text/event-stream"), (
            f"GET {url} expected text/event-stream, got {content_type!r}"
        )
        for chunk in response.iter_text():
            buffer += chunk
            buffer = buffer.replace("\r\n", "\n")
            while "\n\n" in buffer:
                block, buffer = buffer.split("\n\n", 1)
                parsed = _parse_sse_block(block)
                if parsed is None:
                    continue
                events.append(parsed)
                if parsed[0] in TERMINAL_EVENTS:
                    return events
                assert len(events) <= max_events, (
                    f"SSE stream produced more than {max_events} events "
                    "without terminating"
                )
    # Stream closed without an explicit terminal event; keep any trailing block.
    parsed = _parse_sse_block(buffer)
    if parsed is not None:
        events.append(parsed)
    return events


def _assert_stage_event(data: Any, run_id: str) -> None:
    assert isinstance(data, dict), f"stage event data must be a dict, got {data!r}"
    missing = {"run_id", "stage", "status", "detail", "progress"} - data.keys()
    assert not missing, f"stage event missing fields {sorted(missing)}: {data!r}"
    assert data["run_id"] == run_id
    assert data["stage"] in ALLOWED_STAGES, (
        f"stage {data['stage']!r} not in {sorted(ALLOWED_STAGES)}"
    )
    assert data["status"] in ALLOWED_STAGE_STATUSES, (
        f"status {data['status']!r} not in {sorted(ALLOWED_STAGE_STATUSES)}"
    )
    assert isinstance(data["detail"], str)
    progress = data["progress"]
    assert isinstance(progress, (int, float)) and not isinstance(progress, bool), (
        f"progress must be numeric, got {progress!r}"
    )
    assert 0.0 <= float(progress) <= 1.0, f"progress out of range: {progress!r}"


# ---------------------------------------------------------------------------
# Async POST contract
# ---------------------------------------------------------------------------


def test_async_post_returns_202_with_run_id_and_stream_url(client: TestClient):
    payload = _start_async_run(client)

    run_id = payload.get("run_id")
    assert isinstance(run_id, str) and run_id, f"invalid run_id: {run_id!r}"
    assert payload.get("stream_url") == f"/api/sequences/{run_id}/events"


def test_sync_post_without_async_mode_keeps_legacy_shape(client: TestClient):
    response = _post_sequence(client)

    assert response.status_code == 200, (
        "sync POST /api/sequences must stay synchronous (HTTP 200), got "
        f"{response.status_code}: {response.text[:500]}"
    )
    payload = response.json()

    missing = BASELINE_SYNC_RUN_KEYS - payload.keys()
    assert not missing, f"Legacy sync run payload lost keys: {sorted(missing)}"

    assert isinstance(payload["run_id"], str) and payload["run_id"]
    assert payload["status"] in NO_PROVIDER_RUN_STATUSES
    assert isinstance(payload["variants"], list)
    assert len(payload["variants"]) == 2
    # The sync path must not adopt the async response shape.
    assert "stream_url" not in payload


# ---------------------------------------------------------------------------
# SSE streaming
# ---------------------------------------------------------------------------


def test_stream_happy_path_stage_events_and_done(client: TestClient):
    started = _start_async_run(client)
    run_id = started["run_id"]

    events = _collect_sse_events(client, started["stream_url"])
    assert events, "SSE stream produced no events"

    terminal_name, terminal_data = events[-1]
    assert terminal_name == "done", (
        f"expected terminal event 'done', got {terminal_name!r} "
        f"with data {terminal_data!r}"
    )

    stage_events = events[:-1]
    assert stage_events, "expected at least one stage event before 'done'"
    for name, data in stage_events:
        assert name == "stage", f"unexpected event before terminal: {name!r}"
        _assert_stage_event(data, run_id)

    progresses = [float(data["progress"]) for _, data in stage_events]
    assert progresses == sorted(progresses), (
        f"progress must be monotonically non-decreasing, got {progresses}"
    )

    stages_seen = {data["stage"] for _, data in stage_events}
    for required_stage in ("scene_analysis", "render"):
        assert required_stage in stages_seen, (
            f"stage {required_stage!r} missing from stream; saw {sorted(stages_seen)}"
        )

    # The done payload is the same run JSON as the sync POST would return.
    assert isinstance(terminal_data, dict)
    assert terminal_data.get("run_id") == run_id
    assert isinstance(terminal_data.get("variants"), list)
    assert len(terminal_data["variants"]) == 2
    missing = BASELINE_SYNC_RUN_KEYS - terminal_data.keys()
    assert not missing, f"'done' payload missing sync run keys: {sorted(missing)}"


def test_late_subscriber_replays_terminal_event(client: TestClient):
    started = _start_async_run(client)
    run_id = started["run_id"]

    first_pass = _collect_sse_events(client, started["stream_url"])
    assert first_pass and first_pass[-1][0] in TERMINAL_EVENTS

    # Reconnect after completion: the terminal event replays immediately and
    # the stream terminates again.
    replay = _collect_sse_events(client, started["stream_url"])
    assert replay, "late subscriber received no events"
    replay_name, replay_data = replay[-1]
    assert replay_name == first_pass[-1][0]
    assert isinstance(replay_data, dict)
    if replay_name == "done":
        assert replay_data.get("run_id") == run_id


def test_events_unknown_run_id_returns_404(client: TestClient):
    response = client.get("/api/sequences/RUNKNOWN99/events")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Cancellation
# ---------------------------------------------------------------------------


def test_cancel_unknown_run_id_returns_404(client: TestClient):
    response = client.post("/api/sequences/RUNKNOWN99/cancel")
    assert response.status_code == 404


def test_cancel_flow_is_deterministic(client: TestClient):
    """Cancel immediately after starting an async run.

    The run may legitimately finish before the cancel request lands (the
    no-provider pipeline is fast), so both contract outcomes are accepted and
    each is verified strictly:
    - "cancelling"        -> the stream must end with event error, code "cancelled"
    - "already_finished"  -> the stream must replay a terminal event
    No sleeps, no timing races.
    """
    started = _start_async_run(client)
    run_id = started["run_id"]

    cancel = client.post(f"/api/sequences/{run_id}/cancel")
    assert cancel.status_code == 200, (
        f"cancel expected 200, got {cancel.status_code}: {cancel.text[:300]}"
    )
    status = cancel.json().get("status")
    assert status in {"cancelling", "already_finished"}, (
        f"unexpected cancel status: {status!r}"
    )

    events = _collect_sse_events(client, started["stream_url"])
    assert events, "stream after cancel produced no events"
    terminal_name, terminal_data = events[-1]
    assert terminal_name in TERMINAL_EVENTS

    if status == "cancelling":
        assert terminal_name == "error", (
            "a run acknowledged as 'cancelling' must terminate its stream with "
            f"event error, got {terminal_name!r} ({terminal_data!r})"
        )
        assert isinstance(terminal_data, dict)
        assert "message" in terminal_data and "code" in terminal_data
        assert terminal_data["code"] == "cancelled"

    # Once the run is over (cancelled or finished), cancelling again reports
    # already_finished.
    second_cancel = client.post(f"/api/sequences/{run_id}/cancel")
    assert second_cancel.status_code == 200
    assert second_cancel.json().get("status") == "already_finished"
