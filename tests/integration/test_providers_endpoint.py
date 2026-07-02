"""Integration tests for GET /api/providers capability metadata.

Contract under test (additive fields on top of the existing response shape):
- every provider entry includes:
    est_cost_per_second  -> float > 0
    est_wait_seconds     -> int > 0
    lifecycle            -> {"status": <str>, "note": <str>}
- lifecycle.status is one of {"active", "deprecated", "migration_recommended"}
- sora   -> lifecycle.status == "deprecated"
- runway -> lifecycle.status == "migration_recommended"
- all previously existing top-level keys remain present (backward compatibility)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import src.web.persistence as persistence
from src.web.app import app
from src.web.persistence import SUPPORTED_PROVIDERS

ALLOWED_LIFECYCLE_STATUSES = {"active", "deprecated", "migration_recommended"}

# Baseline top-level keys of the /api/providers payload before the capability
# metadata extension (derived from the pre-existing handler in src/web/app.py).
BASELINE_PROVIDERS_KEYS = {
    "available_providers",
    "provider_count",
    "supported_providers",
    "credential_status",
    "defaults",
}
BASELINE_DEFAULTS_KEYS = {"preset_default", "aspect_ratio", "duration", "variants"}


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


def _get_providers_payload(client: TestClient) -> dict[str, Any]:
    response = client.get("/api/providers")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    return payload


def _extract_capability_entries(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Locate the per-provider capability metadata in the response payload.

    The fields are additive, so this tolerates either container shape:
    - a dict mapping provider name -> metadata entry, or
    - a list of metadata entries carrying a provider identifier key.
    """
    for value in payload.values():
        if isinstance(value, dict):
            entries = {
                name: entry
                for name, entry in value.items()
                if isinstance(entry, dict) and "est_cost_per_second" in entry
            }
            if entries:
                return entries
        if isinstance(value, list):
            entries = {}
            for entry in value:
                if not (isinstance(entry, dict) and "est_cost_per_second" in entry):
                    continue
                name = entry.get("provider") or entry.get("name") or entry.get("id")
                if name:
                    entries[name] = entry
            if entries:
                return entries

    pytest.fail(
        "No per-provider capability metadata (est_cost_per_second et al.) found "
        f"in /api/providers payload. Top-level keys: {sorted(payload.keys())}"
    )


def test_providers_returns_200_and_dict(client: TestClient):
    payload = _get_providers_payload(client)
    assert isinstance(payload["supported_providers"], list)


def test_providers_backward_compatible_keys(client: TestClient):
    payload = _get_providers_payload(client)

    missing = BASELINE_PROVIDERS_KEYS - payload.keys()
    assert not missing, f"Baseline keys missing from /api/providers: {sorted(missing)}"

    assert isinstance(payload["available_providers"], list)
    assert isinstance(payload["provider_count"], int)
    assert payload["provider_count"] == len(payload["available_providers"])
    assert set(payload["supported_providers"]) == set(SUPPORTED_PROVIDERS)

    defaults = payload["defaults"]
    assert isinstance(defaults, dict)
    missing_defaults = BASELINE_DEFAULTS_KEYS - defaults.keys()
    assert not missing_defaults, f"Baseline defaults keys missing: {sorted(missing_defaults)}"


def test_every_provider_entry_has_capability_metadata(client: TestClient):
    payload = _get_providers_payload(client)
    entries = _extract_capability_entries(payload)

    missing_providers = set(SUPPORTED_PROVIDERS) - entries.keys()
    assert not missing_providers, (
        f"Capability metadata missing for providers: {sorted(missing_providers)}"
    )

    for provider, entry in entries.items():
        cost = entry.get("est_cost_per_second")
        assert isinstance(cost, (int, float)) and not isinstance(cost, bool), (
            f"{provider}: est_cost_per_second must be numeric, got {cost!r}"
        )
        assert cost > 0, f"{provider}: est_cost_per_second must be > 0, got {cost!r}"

        wait = entry.get("est_wait_seconds")
        assert isinstance(wait, int) and not isinstance(wait, bool), (
            f"{provider}: est_wait_seconds must be an int, got {wait!r}"
        )
        assert wait > 0, f"{provider}: est_wait_seconds must be > 0, got {wait!r}"

        lifecycle = entry.get("lifecycle")
        assert isinstance(lifecycle, dict), (
            f"{provider}: lifecycle must be a dict, got {lifecycle!r}"
        )
        assert "status" in lifecycle and "note" in lifecycle, (
            f"{provider}: lifecycle must contain 'status' and 'note', got {lifecycle!r}"
        )
        assert lifecycle["status"] in ALLOWED_LIFECYCLE_STATUSES, (
            f"{provider}: lifecycle.status {lifecycle['status']!r} not in "
            f"{sorted(ALLOWED_LIFECYCLE_STATUSES)}"
        )


def test_sora_lifecycle_is_deprecated(client: TestClient):
    payload = _get_providers_payload(client)
    entries = _extract_capability_entries(payload)
    if "sora" not in entries:
        pytest.skip("sora provider not present in capability metadata")
    assert entries["sora"]["lifecycle"]["status"] == "deprecated"


def test_runway_lifecycle_is_migration_recommended(client: TestClient):
    payload = _get_providers_payload(client)
    entries = _extract_capability_entries(payload)
    if "runway" not in entries:
        pytest.skip("runway provider not present in capability metadata")
    assert entries["runway"]["lifecycle"]["status"] == "migration_recommended"


def test_non_flagged_providers_are_active(client: TestClient):
    payload = _get_providers_payload(client)
    entries = _extract_capability_entries(payload)
    for provider, entry in entries.items():
        if provider in {"sora", "runway"}:
            continue
        assert entry["lifecycle"]["status"] == "active", (
            f"{provider}: expected lifecycle.status 'active', "
            f"got {entry['lifecycle']['status']!r}"
        )


def test_health_returns_200(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
