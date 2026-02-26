from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import src.web.persistence as persistence
from src.web.app import app


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


def _bootstrap_owner_key(client: TestClient) -> str:
    response = client.get("/api/session/bootstrap")
    assert response.status_code == 200
    session_id = client.cookies.get(persistence.SESSION_COOKIE_NAME)
    assert session_id
    session = persistence.get_or_create_session(session_id)
    return session["owner_key"]


def test_session_bootstrap_and_settings_versioning(client: TestClient):
    bootstrap = client.get("/api/session/bootstrap")
    assert bootstrap.status_code == 200
    assert bootstrap.json()["authenticated"] is False
    assert client.cookies.get(persistence.SESSION_COOKIE_NAME)

    settings_response = client.get("/api/settings")
    assert settings_response.status_code == 200
    assert settings_response.json()["version"] == 1

    updated_payload = settings_response.json()["settings"]
    updated_payload["theme"]["accent"] = "teal"
    save_response = client.put(
        "/api/settings",
        json={"settings": updated_payload, "change_note": "test_theme_change"},
    )
    assert save_response.status_code == 200
    assert save_response.json()["version"] == 2

    history_response = client.get("/api/settings/history")
    assert history_response.status_code == 200
    history = history_response.json()["history"]
    assert len(history) >= 2
    assert history[0]["change_note"] in {"test_theme_change", "update"}

    first_version = next(entry for entry in history if entry["version"] == 1)
    restore_response = client.post(f"/api/settings/history/{first_version['id']}/restore")
    assert restore_response.status_code == 200
    assert restore_response.json()["version"] == 3

    final_settings = client.get("/api/settings").json()["settings"]
    assert final_settings["theme"]["accent"] == "amber"


def test_api_key_management_affects_provider_availability(client: TestClient):
    baseline = client.get("/api/providers")
    assert baseline.status_code == 200
    assert "runway" not in baseline.json()["available_providers"]

    invalid_save = client.put("/api/settings/api-keys/runway", json={"api_key": "short"})
    assert invalid_save.status_code == 400

    save = client.put(
        "/api/settings/api-keys/runway",
        json={"api_key": "rk_test_key_1234567890"},
    )
    assert save.status_code == 200
    assert save.json()["configured"] is True
    assert save.json()["provider"] == "runway"

    providers = client.get("/api/providers")
    assert providers.status_code == 200
    assert "runway" in providers.json()["available_providers"]

    key_status = client.get("/api/settings/api-keys")
    assert key_status.status_code == 200
    runway = next(row for row in key_status.json()["api_keys"] if row["provider"] == "runway")
    assert runway["configured"] is True
    assert runway["masked"].startswith("rk_t")

    deleted = client.delete("/api/settings/api-keys/runway")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True

    providers_after_delete = client.get("/api/providers")
    assert providers_after_delete.status_code == 200
    assert "runway" not in providers_after_delete.json()["available_providers"]


def test_runs_list_update_clear_and_backup_restore(client: TestClient):
    owner_key = _bootstrap_owner_key(client)
    run_id = "RTEST1234"
    run_payload = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "not_configured",
        "intent": "Static camera test",
        "preset": "cinematic-balanced",
        "params": {
            "duration": 6,
            "variants": 3,
            "aspect_ratio": "16:9",
            "motion_intensity": 4,
            "quality_mode": "balanced",
            "provider": None,
            "provider_requested": "auto",
        },
        "source_image": {"filename": "sample.jpg", "content_type": "image/jpeg", "bytes": 123},
        "analysis": {"object_count": 0},
        "available_providers": [],
        "variants": [],
    }
    persistence.save_run(owner_key, run_payload)

    runs = client.get("/api/runs")
    assert runs.status_code == 200
    assert len(runs.json()["runs"]) == 1
    assert runs.json()["runs"][0]["run_id"] == run_id

    run_payload["status"] = "success"
    update = client.put(f"/api/runs/{run_id}", json=run_payload)
    assert update.status_code == 200
    assert update.json()["updated"] is True

    backup = client.get("/api/settings/backup")
    assert backup.status_code == 200
    backup_payload = backup.json()
    assert backup_payload["settings"]["version"] >= 1
    assert len(backup_payload["runs"]) == 1

    cleared = client.delete("/api/runs")
    assert cleared.status_code == 200
    assert cleared.json()["deleted_runs"] == 1
    assert client.get("/api/runs").json()["runs"] == []

    restored = client.post("/api/settings/restore", json=backup_payload)
    assert restored.status_code == 200
    assert restored.json()["restored_runs"] == 1

    runs_after_restore = client.get("/api/runs")
    assert runs_after_restore.status_code == 200
    assert len(runs_after_restore.json()["runs"]) == 1
    assert runs_after_restore.json()["runs"][0]["status"] == "success"


def test_restore_accepts_legacy_localstorage_payload_shape(client: TestClient):
    _bootstrap_owner_key(client)
    legacy_payload = {
        "animatize_ui_settings_v2": {
            "accessibility": {
                "reducedMotion": True,
                "highContrastFocus": True,
                "announceStatusChanges": False,
            },
            "preferences": {
                "autoFavoriteWinner": True,
                "defaultPreset": "speed-first",
                "defaultAspectRatio": "9:16",
                "defaultDuration": 8,
                "defaultVariants": 4,
            },
            "behavior": {
                "autoSave": True,
                "autoSaveDelayMs": 900,
                "renderQuality": "fast",
                "parallelPreviews": 1,
                "confirmBeforeClear": False,
            },
            "theme": {
                "mode": "darkroom",
                "accent": "crimson",
                "grain": 0.5,
                "contrast": 1.1,
                "density": "comfortable",
            },
            "developer": {
                "showRawPayload": True,
                "enableDebugOverlay": True,
                "enableKeyboardTimeline": True,
                "gestureNavigation": True,
            },
        },
        "animatize_ui_runs_v2": [
            {
                "run_id": "RLEGACY1",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "not_executed",
                "intent": "Legacy import run",
                "preset": "speed-first",
                "params": {
                    "duration": 8,
                    "variants": 4,
                    "aspect_ratio": "9:16",
                    "motion_intensity": 5,
                    "quality_mode": "fast",
                    "provider": None,
                    "provider_requested": "auto",
                },
                "source_image": {"filename": "legacy.jpg", "content_type": "image/jpeg", "bytes": 99},
                "analysis": {"object_count": 1},
                "available_providers": [],
                "variants": [],
            }
        ],
    }

    restore = client.post("/api/settings/restore", json=legacy_payload)
    assert restore.status_code == 200
    assert restore.json()["restored_runs"] == 1

    settings = client.get("/api/settings").json()["settings"]
    assert settings["theme"]["accent"] == "crimson"
    assert settings["preferences"]["defaultPreset"] == "speed-first"

    runs = client.get("/api/runs").json()["runs"]
    assert len(runs) == 1
    assert runs[0]["run_id"] == "RLEGACY1"
