from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"


def _default_db_path() -> Path:
    env_path = os.getenv("ANIMATIZE_WEB_DB_PATH", "").strip()
    if env_path:
        return Path(env_path)

    # Vercel serverless filesystem is read-only except /tmp.
    if os.getenv("VERCEL", "").strip():
        return Path("/tmp/animatize_web.db")

    return DATA_DIR / "animatize_web.db"


DB_PATH = _default_db_path()
if not str(DB_PATH).startswith("/tmp"):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fallback for read-only runtimes.
        DB_PATH = Path("/tmp/animatize_web.db")

SESSION_COOKIE_NAME = "animatize_session"
SESSION_TTL_HOURS = int(os.getenv("ANIMATIZE_SESSION_TTL_HOURS", "720"))

SUPPORTED_PROVIDERS = ("runway", "pika", "veo", "sora", "flux")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_expiry_iso() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)).isoformat()


def _connection() -> sqlite3.Connection:
    global DB_PATH
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        DB_PATH = Path("/tmp/animatize_web.db")
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _owner_key(user_id: str | None, guest_id: str | None) -> str:
    if user_id:
        return f"user:{user_id}"
    if guest_id:
        return f"guest:{guest_id}"
    return "guest:anonymous"


def _default_settings() -> dict[str, Any]:
    return {
        "accessibility": {
            "reducedMotion": False,
            "highContrastFocus": True,
            "announceStatusChanges": True,
        },
        "preferences": {
            "autoFavoriteWinner": False,
            "defaultPreset": "cinematic-balanced",
            "defaultAspectRatio": "16:9",
            "defaultDuration": 6,
            "defaultVariants": 3,
        },
        "behavior": {
            "autoSave": True,
            "autoSaveDelayMs": 700,
            "renderQuality": "balanced",
            "parallelPreviews": 2,
            "confirmBeforeClear": True,
        },
        "theme": {
            "mode": "darkroom",
            "accent": "amber",
            "grain": 0.35,
            "contrast": 1.0,
            "density": "comfortable",
        },
        "developer": {
            "showRawPayload": False,
            "enableDebugOverlay": False,
            "enableKeyboardTimeline": True,
            "gestureNavigation": True,
        },
    }


def _fernet() -> Fernet:
    secret = os.getenv("ANIMATIZE_SECRET_KEY", "animatize-dev-secret-change-me")
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def _encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def _decrypt(value: str) -> str:
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def init_db() -> None:
    with _connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                name TEXT,
                picture TEXT,
                provider TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                guest_id TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE TABLE IF NOT EXISTS settings_profiles (
                owner_key TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                version INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_key TEXT NOT NULL,
                version INTEGER NOT NULL,
                payload TEXT NOT NULL,
                change_note TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS generation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_key TEXT NOT NULL,
                run_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                payload TEXT NOT NULL,
                UNIQUE(owner_key, run_id)
            );

            CREATE TABLE IF NOT EXISTS api_credentials (
                owner_key TEXT NOT NULL,
                provider TEXT NOT NULL,
                encrypted_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (owner_key, provider)
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_settings_history_owner_key ON settings_history(owner_key);
            CREATE INDEX IF NOT EXISTS idx_generation_runs_owner_key ON generation_runs(owner_key);
            CREATE INDEX IF NOT EXISTS idx_generation_runs_created_at ON generation_runs(created_at);
            """
        )


def _purge_expired_sessions(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (_now_iso(),))


def create_guest_session() -> dict[str, Any]:
    session_id = uuid.uuid4().hex
    guest_id = f"g_{uuid.uuid4().hex[:12]}"
    now = _now_iso()
    with _connection() as conn:
        _purge_expired_sessions(conn)
        conn.execute(
            """
            INSERT INTO sessions (session_id, user_id, guest_id, created_at, expires_at, last_seen_at)
            VALUES (?, NULL, ?, ?, ?, ?)
            """,
            (session_id, guest_id, now, _session_expiry_iso(), now),
        )
    return {
        "session_id": session_id,
        "user_id": None,
        "guest_id": guest_id,
        "owner_key": _owner_key(None, guest_id),
        "is_new": True,
    }


def get_or_create_session(session_id: str | None) -> dict[str, Any]:
    if not session_id:
        return create_guest_session()

    with _connection() as conn:
        row = conn.execute(
            "SELECT session_id, user_id, guest_id FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return create_guest_session()
        return {
            "session_id": row["session_id"],
            "user_id": row["user_id"],
            "guest_id": row["guest_id"],
            "owner_key": _owner_key(row["user_id"], row["guest_id"]),
            "is_new": False,
        }


def rotate_guest_session(session_id: str | None) -> dict[str, Any]:
    if session_id:
        with _connection() as conn:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    return create_guest_session()


def attach_user_to_session(session_id: str, *, email: str, name: str, picture: str | None, provider: str = "google") -> dict[str, Any]:
    now = _now_iso()
    user_id = f"u_{hashlib.sha256(email.lower().encode('utf-8')).hexdigest()[:20]}"
    with _connection() as conn:
        conn.execute(
            """
            INSERT INTO users (id, email, name, picture, provider, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name = excluded.name,
                picture = excluded.picture,
                provider = excluded.provider,
                updated_at = excluded.updated_at
            """,
            (user_id, email, name, picture, provider, now, now),
        )

        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        resolved_user_id = row["id"] if row else user_id

        conn.execute(
            """
            UPDATE sessions
            SET user_id = ?, guest_id = NULL, last_seen_at = ?, expires_at = ?
            WHERE session_id = ?
            """,
            (resolved_user_id, now, _session_expiry_iso(), session_id),
        )

    return {
        "session_id": session_id,
        "user_id": resolved_user_id,
        "guest_id": None,
        "owner_key": _owner_key(resolved_user_id, None),
        "is_new": False,
        "user": {
            "id": resolved_user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "provider": provider,
        },
    }


def get_user_for_session(session_id: str) -> dict[str, Any] | None:
    with _connection() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.email, u.name, u.picture, u.provider
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.session_id = ?
            """,
            (session_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "picture": row["picture"],
        "provider": row["provider"],
    }


def get_settings(owner_key: str) -> dict[str, Any]:
    with _connection() as conn:
        row = conn.execute(
            "SELECT payload, version, created_at, updated_at FROM settings_profiles WHERE owner_key = ?",
            (owner_key,),
        ).fetchone()

        if not row:
            now = _now_iso()
            payload = _default_settings()
            conn.execute(
                """
                INSERT INTO settings_profiles (owner_key, payload, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (owner_key, json.dumps(payload), 1, now, now),
            )
            conn.execute(
                """
                INSERT INTO settings_history (owner_key, version, payload, change_note, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (owner_key, 1, json.dumps(payload), "initial_profile", now),
            )
            return {
                "settings": payload,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            }

        return {
            "settings": json.loads(row["payload"]),
            "version": row["version"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


def save_settings(owner_key: str, settings: dict[str, Any], change_note: str = "update") -> dict[str, Any]:
    current = get_settings(owner_key)
    next_version = int(current["version"]) + 1
    now = _now_iso()

    with _connection() as conn:
        conn.execute(
            """
            UPDATE settings_profiles
            SET payload = ?, version = ?, updated_at = ?
            WHERE owner_key = ?
            """,
            (json.dumps(settings), next_version, now, owner_key),
        )
        conn.execute(
            """
            INSERT INTO settings_history (owner_key, version, payload, change_note, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (owner_key, next_version, json.dumps(settings), change_note, now),
        )

    return {
        "settings": settings,
        "version": next_version,
        "updated_at": now,
    }


def list_settings_history(owner_key: str, limit: int = 25) -> list[dict[str, Any]]:
    capped = max(1, min(limit, 100))
    with _connection() as conn:
        rows = conn.execute(
            """
            SELECT id, version, payload, change_note, created_at
            FROM settings_history
            WHERE owner_key = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (owner_key, capped),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "version": row["version"],
            "settings": json.loads(row["payload"]),
            "change_note": row["change_note"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def restore_settings_version(owner_key: str, history_id: int) -> dict[str, Any]:
    with _connection() as conn:
        row = conn.execute(
            """
            SELECT payload
            FROM settings_history
            WHERE owner_key = ? AND id = ?
            """,
            (owner_key, history_id),
        ).fetchone()

    if not row:
        raise ValueError("Settings version not found.")

    payload = json.loads(row["payload"])
    return save_settings(owner_key, payload, change_note=f"restore:{history_id}")


def save_run(owner_key: str, run_payload: dict[str, Any]) -> None:
    run_id = run_payload.get("run_id")
    if not run_id:
        return
    created_at = run_payload.get("created_at", _now_iso())
    with _connection() as conn:
        conn.execute(
            """
            INSERT INTO generation_runs (owner_key, run_id, created_at, payload)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(owner_key, run_id) DO UPDATE SET
                payload = excluded.payload,
                created_at = excluded.created_at
            """,
            (owner_key, run_id, created_at, json.dumps(run_payload)),
        )


def update_run(owner_key: str, run_id: str, run_payload: dict[str, Any]) -> bool:
    with _connection() as conn:
        cursor = conn.execute(
            """
            UPDATE generation_runs
            SET payload = ?, created_at = ?
            WHERE owner_key = ? AND run_id = ?
            """,
            (
                json.dumps(run_payload),
                run_payload.get("created_at", _now_iso()),
                owner_key,
                run_id,
            ),
        )
    return cursor.rowcount > 0


def list_runs(owner_key: str, limit: int = 100) -> list[dict[str, Any]]:
    capped = max(1, min(limit, 300))
    with _connection() as conn:
        rows = conn.execute(
            """
            SELECT payload
            FROM generation_runs
            WHERE owner_key = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (owner_key, capped),
        ).fetchall()
    return [json.loads(row["payload"]) for row in rows]


def clear_runs(owner_key: str) -> int:
    with _connection() as conn:
        cursor = conn.execute("DELETE FROM generation_runs WHERE owner_key = ?", (owner_key,))
    return cursor.rowcount


def set_provider_api_key(owner_key: str, provider: str, api_key: str) -> dict[str, Any]:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'.")
    if not api_key or len(api_key.strip()) < 8:
        raise ValueError("API key is too short.")

    now = _now_iso()
    encrypted = _encrypt(api_key.strip())
    with _connection() as conn:
        conn.execute(
            """
            INSERT INTO api_credentials (owner_key, provider, encrypted_key, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(owner_key, provider) DO UPDATE SET
                encrypted_key = excluded.encrypted_key,
                updated_at = excluded.updated_at
            """,
            (owner_key, provider, encrypted, now, now),
        )

    return {
        "provider": provider,
        "configured": True,
        "masked": _mask_api_key(api_key),
        "updated_at": now,
    }


def delete_provider_api_key(owner_key: str, provider: str) -> bool:
    with _connection() as conn:
        cursor = conn.execute(
            "DELETE FROM api_credentials WHERE owner_key = ? AND provider = ?",
            (owner_key, provider),
        )
    return cursor.rowcount > 0


def get_provider_keys(owner_key: str) -> dict[str, str]:
    with _connection() as conn:
        rows = conn.execute(
            "SELECT provider, encrypted_key FROM api_credentials WHERE owner_key = ?",
            (owner_key,),
        ).fetchall()

    resolved: dict[str, str] = {}
    for row in rows:
        try:
            resolved[row["provider"]] = _decrypt(row["encrypted_key"])
        except Exception:
            continue
    return resolved


def list_provider_key_status(owner_key: str) -> list[dict[str, Any]]:
    with _connection() as conn:
        rows = conn.execute(
            "SELECT provider, encrypted_key, updated_at FROM api_credentials WHERE owner_key = ?",
            (owner_key,),
        ).fetchall()

    status_map: dict[str, dict[str, Any]] = {
        provider: {
            "provider": provider,
            "configured": False,
            "masked": None,
            "updated_at": None,
        }
        for provider in SUPPORTED_PROVIDERS
    }

    for row in rows:
        provider = row["provider"]
        try:
            raw = _decrypt(row["encrypted_key"])
            masked = _mask_api_key(raw)
        except Exception:
            masked = "corrupted"
        status_map[provider] = {
            "provider": provider,
            "configured": True,
            "masked": masked,
            "updated_at": row["updated_at"],
        }

    return list(status_map.values())


def export_bundle(owner_key: str) -> dict[str, Any]:
    profile = get_settings(owner_key)
    history = list_settings_history(owner_key, limit=100)
    runs = list_runs(owner_key, limit=300)
    credentials = list_provider_key_status(owner_key)

    return {
        "schema_version": "2026-02-26",
        "exported_at": _now_iso(),
        "settings": profile,
        "history": history,
        "runs": runs,
        "api_credentials": credentials,
    }


def restore_bundle(owner_key: str, bundle: dict[str, Any]) -> dict[str, Any]:
    settings_payload: dict[str, Any] | None = None
    settings_block = bundle.get("settings")
    if isinstance(settings_block, dict):
        if isinstance(settings_block.get("settings"), dict):
            settings_payload = settings_block["settings"]
        else:
            # Legacy import format: top-level settings object from localStorage.
            settings_payload = settings_block
    elif isinstance(bundle.get("animatize_ui_settings_v2"), dict):
        settings_payload = bundle["animatize_ui_settings_v2"]

    if not isinstance(settings_payload, dict):
        raise ValueError(
            "Restore payload is missing a valid settings object "
            "(expected settings.settings or legacy settings)."
        )

    restored = save_settings(owner_key, settings_payload, change_note="restore:bundle")

    runs = bundle.get("runs")
    if not isinstance(runs, list):
        runs = bundle.get("animatize_ui_runs_v2")
    if not isinstance(runs, list):
        runs = []
    restored_runs = 0
    if isinstance(runs, list):
        for run in runs:
            if isinstance(run, dict) and run.get("run_id"):
                save_run(owner_key, run)
                restored_runs += 1

    return {
        "settings": restored,
        "restored_runs": restored_runs,
        "restored_at": _now_iso(),
    }


def _mask_api_key(value: str) -> str:
    stripped = value.strip()
    if len(stripped) <= 8:
        return "*" * len(stripped)
    return f"{stripped[:4]}{'*' * (len(stripped) - 8)}{stripped[-4:]}"


# Ensure schema exists even when functions are called outside FastAPI startup hooks.
init_db()
