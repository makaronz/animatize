from __future__ import annotations

import math
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from src.adapters.contracts import ProviderType
from src.analyzers.video_prompt_analyzer import CameraMotion, ModelType
from src.core.video_pipeline import PipelineConfig, VideoGenerationPipeline
from src.generators.video_prompt_generator import (
    DeterminismConfig,
    VideoControlParameters,
    VideoGenerationRequest,
    VideoPromptCompiler,
)
from src.web.persistence import (
    SESSION_COOKIE_NAME,
    SESSION_TTL_HOURS,
    SUPPORTED_PROVIDERS,
    attach_user_to_session,
    clear_runs,
    delete_provider_api_key,
    export_bundle,
    get_or_create_session,
    get_provider_keys,
    get_settings,
    get_user_for_session,
    init_db,
    list_provider_key_status,
    list_runs,
    list_settings_history,
    restore_bundle,
    restore_settings_version,
    rotate_guest_session,
    save_run,
    save_settings,
    set_provider_api_key,
    update_run,
)


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
STATIC_DIR = BASE_DIR / "static"
CONFIG_DIR = REPO_ROOT / "configs"


def _iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_safe(value: Any) -> Any:
    """Convert nested payloads into RFC8259-safe JSON values."""
    if value is None or isinstance(value, (str, bool, int)):
        return value

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {str(key): _json_safe(inner) for key, inner in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_json_safe(inner) for inner in value]

    # numpy scalar compatibility without hard dependency on numpy
    if hasattr(value, "item") and callable(value.item):
        try:
            return _json_safe(value.item())
        except Exception:
            pass

    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            return _json_safe(value.to_dict())
        except Exception:
            pass

    return str(value)


def _cookie_secure() -> bool:
    return os.getenv("ANIMATIZE_COOKIE_SECURE", "false").lower() == "true"


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_id,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        max_age=SESSION_TTL_HOURS * 3600,
    )


def _resolve_session(request: Request) -> tuple[dict[str, Any], bool]:
    incoming = request.cookies.get(SESSION_COOKIE_NAME)
    session = get_or_create_session(incoming)
    should_set_cookie = bool(session.get("is_new")) or incoming != session.get("session_id")
    return session, should_set_cookie


def _session_response(payload: dict[str, Any], session: dict[str, Any], should_set_cookie: bool) -> JSONResponse:
    response = JSONResponse(payload)
    if should_set_cookie:
        _set_session_cookie(response, session["session_id"])
    return response


def _provider_env_map(owner_key: str | None = None) -> dict[str, str]:
    env_map = {
        "runway": os.getenv("RUNWAY_API_KEY", "").strip(),
        "pika": os.getenv("PIKA_API_KEY", "").strip(),
        "veo": os.getenv("VEO_API_KEY", "").strip(),
        "sora": os.getenv("SORA_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip(),
        "flux": os.getenv("FLUX_API_KEY", "").strip(),
    }

    if owner_key:
        user_keys = get_provider_keys(owner_key)
        for provider, key in user_keys.items():
            if key:
                env_map[provider] = key.strip()

    return env_map


def _available_providers(owner_key: str | None = None) -> list[str]:
    return [provider for provider, key in _provider_env_map(owner_key).items() if key]


def _resolve_provider(requested: str, available: list[str], preset: str) -> str | None:
    if requested and requested != "auto":
        if requested in available:
            return requested
        return None
    if not available:
        return None
    preset_map = {
        "coherence-first": "runway",
        "speed-first": "pika",
        "cinematic-balanced": "runway",
    }
    target = preset_map.get(preset, "runway")
    if target in available:
        return target
    return available[0]


def _provider_type(provider: str) -> ProviderType:
    mapping = {
        "runway": ProviderType.RUNWAY,
        "pika": ProviderType.PIKA,
        "veo": ProviderType.VEO,
        "sora": ProviderType.SORA,
        "flux": ProviderType.FLUX,
    }
    return mapping[provider]


def _model_for_provider(provider: str) -> str:
    return {
        "runway": "gen3",
        "pika": "pika-2.2",
        "veo": "veo-3.0-generate-preview",
        "sora": "sora-2",
        "flux": "flux-pro",
    }[provider]


def _model_type_for_provider(provider: str) -> ModelType:
    return {
        "runway": ModelType.RUNWAY,
        "pika": ModelType.PIKA,
        "veo": ModelType.VEO3,
        "sora": ModelType.SORA2,
        "flux": ModelType.LTX2,
    }[provider]


def _resolution_for(aspect_ratio: str, quality: str) -> tuple[int, int]:
    if quality == "high":
        table = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1": (1280, 1280),
            "4:5": (1080, 1350),
        }
    elif quality == "fast":
        table = {
            "16:9": (960, 540),
            "9:16": (540, 960),
            "1:1": (768, 768),
            "4:5": (768, 960),
        }
    else:
        table = {
            "16:9": (1280, 720),
            "9:16": (720, 1280),
            "1:1": (1024, 1024),
            "4:5": (960, 1200),
        }
    return table.get(aspect_ratio, (1280, 720))


def _parse_variant_count(raw: int) -> int:
    return max(2, min(raw, 5))


def _build_pipeline(owner_key: str | None = None) -> VideoGenerationPipeline:
    pipeline = VideoGenerationPipeline(
        config=PipelineConfig(
            enable_cache=True,
            cache_ttl=3600,
            cache_max_size=500,
            enable_metrics=True,
            default_timeout=600,
        )
    )
    key_map = _provider_env_map(owner_key)
    if key_map["runway"]:
        pipeline.register_runway_adapter(key_map["runway"])
    if key_map["pika"]:
        pipeline.register_pika_adapter(key_map["pika"])
    if key_map["veo"]:
        pipeline.register_veo_adapter(key_map["veo"])
    if key_map["sora"]:
        pipeline.register_sora_adapter(key_map["sora"])
    if key_map["flux"]:
        pipeline.register_flux_adapter(key_map["flux"])
    return pipeline


def _provider_parameters(
    provider: str,
    compiled_parameters: dict[str, Any],
    duration: float,
    aspect_ratio: str,
    quality_mode: str,
    motion_intensity: int,
    negative_intent: str,
) -> dict[str, Any]:
    width, height = _resolution_for(aspect_ratio, quality_mode)
    base = {
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "fps": int(compiled_parameters.get("fps", 24)),
        "motion_strength": max(0.1, min(motion_intensity / 10.0, 1.0)),
        "seed": compiled_parameters.get("seed"),
    }

    if negative_intent:
        base["negative_prompt"] = negative_intent

    if provider == "runway":
        base.update(
            {
                "resolution": f"{width}x{height}",
                "gen_version": "gen3",
            }
        )
    elif provider == "sora":
        base.update(
            {
                "size": f"{width}x{height}",
                "quality": "high" if quality_mode == "high" else "standard",
            }
        )
    elif provider == "veo":
        base.update({"model": "veo-3.0-generate-preview"})
    elif provider == "pika":
        base.update({"aspect_ratio": aspect_ratio})
    elif provider == "flux":
        base.update(
            {
                "width": width,
                "height": height,
                "guidance_scale": compiled_parameters.get("guidance_scale", 7.5),
                "steps": 40,
            }
        )
    return base


def _variant_camera(index: int, motion_strength: float) -> CameraMotion:
    motions = [
        CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50),
        CameraMotion(type="pan", speed="slow", direction="right", focal_length=35),
        CameraMotion(type="orbit", speed="medium", direction="left", focal_length=35),
        CameraMotion(type="zoom", speed="slow", direction="in", focal_length=70),
        CameraMotion(type="crane", speed="slow", direction="up", focal_length=50),
    ]
    motion = motions[index % len(motions)]
    motion.speed = "medium" if motion_strength > 0.7 else motion.speed
    return motion


app = FastAPI(
    title="ANIMAtiZE Director Console",
    description="Cinematic workflow UI with persistent settings, auth, and generation orchestration.",
    version="0.3.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/")
async def index(request: Request) -> FileResponse:
    session, should_set_cookie = _resolve_session(request)
    response = FileResponse(STATIC_DIR / "index.html")
    if should_set_cookie:
        _set_session_cookie(response, session["session_id"])
    return response


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "timestamp": _iso_utc()})


@app.get("/api/session/bootstrap")
async def session_bootstrap(request: Request) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    user = get_user_for_session(session["session_id"]) if session.get("user_id") else None
    return _session_response(
        {
            "session_id": session["session_id"],
            "authenticated": bool(user),
            "user": user,
        },
        session,
        should_set_cookie,
    )


@app.get("/api/auth/config")
async def auth_config() -> JSONResponse:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    return JSONResponse(
        {
            "google_enabled": bool(client_id),
            "google_client_id": client_id or None,
        }
    )


@app.get("/api/auth/me")
async def auth_me(request: Request) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    user = get_user_for_session(session["session_id"]) if session.get("user_id") else None
    return _session_response(
        {
            "authenticated": bool(user),
            "user": user,
        },
        session,
        should_set_cookie,
    )


@app.post("/api/auth/google")
async def auth_google(request: Request, payload: dict[str, Any] = Body(...)) -> JSONResponse:
    credential = str(payload.get("credential", "")).strip()
    if not credential:
        raise HTTPException(status_code=400, detail="Google credential is required.")

    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        raise HTTPException(status_code=503, detail="Google auth is not configured on this runtime.")

    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token
    except ImportError as error:
        raise HTTPException(
            status_code=503,
            detail="google-auth package is required for Google sign-in verification.",
        ) from error

    try:
        token_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            audience=client_id,
        )
    except Exception as error:
        raise HTTPException(status_code=401, detail=f"Google token verification failed: {error}") from error

    email = str(token_info.get("email", "")).strip().lower()
    name = str(token_info.get("name", "")).strip() or email.split("@")[0]
    picture = token_info.get("picture")
    if not email:
        raise HTTPException(status_code=401, detail="Google token did not include an email address.")

    session, _ = _resolve_session(request)
    attached = attach_user_to_session(
        session["session_id"],
        email=email,
        name=name,
        picture=picture,
        provider="google",
    )

    response = JSONResponse(
        {
            "authenticated": True,
            "user": attached["user"],
        }
    )
    _set_session_cookie(response, attached["session_id"])
    return response


@app.post("/api/auth/logout")
async def auth_logout(request: Request) -> JSONResponse:
    incoming = request.cookies.get(SESSION_COOKIE_NAME)
    session = rotate_guest_session(incoming)
    response = JSONResponse(
        {
            "authenticated": False,
            "user": None,
        }
    )
    _set_session_cookie(response, session["session_id"])
    return response


@app.get("/api/settings")
async def get_settings_endpoint(request: Request) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    profile = get_settings(session["owner_key"])
    return _session_response(profile, session, should_set_cookie)


@app.put("/api/settings")
async def save_settings_endpoint(request: Request, payload: dict[str, Any] = Body(...)) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    settings_payload = payload.get("settings")
    if not isinstance(settings_payload, dict):
        raise HTTPException(status_code=400, detail="Body must include a settings object.")

    change_note = str(payload.get("change_note", "autosave"))
    saved = save_settings(session["owner_key"], settings_payload, change_note=change_note)
    return _session_response(saved, session, should_set_cookie)


@app.get("/api/settings/history")
async def settings_history_endpoint(request: Request, limit: int = Query(25, ge=1, le=100)) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    history = list_settings_history(session["owner_key"], limit=limit)
    return _session_response({"history": history}, session, should_set_cookie)


@app.post("/api/settings/history/{history_id}/restore")
async def settings_restore_version(request: Request, history_id: int) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    try:
        restored = restore_settings_version(session["owner_key"], history_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return _session_response(restored, session, should_set_cookie)


@app.get("/api/settings/api-keys")
async def list_api_keys_endpoint(request: Request) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    status_rows = list_provider_key_status(session["owner_key"])
    return _session_response({"api_keys": status_rows}, session, should_set_cookie)


@app.put("/api/settings/api-keys/{provider}")
async def set_api_key_endpoint(request: Request, provider: str, payload: dict[str, Any] = Body(...)) -> JSONResponse:
    provider = provider.strip().lower()
    session, should_set_cookie = _resolve_session(request)

    api_key = str(payload.get("api_key", "")).strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key is required.")

    try:
        result = set_provider_api_key(session["owner_key"], provider, api_key)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return _session_response(result, session, should_set_cookie)


@app.delete("/api/settings/api-keys/{provider}")
async def delete_api_key_endpoint(request: Request, provider: str) -> JSONResponse:
    provider = provider.strip().lower()
    session, should_set_cookie = _resolve_session(request)

    deleted = delete_provider_api_key(session["owner_key"], provider)
    return _session_response(
        {
            "provider": provider,
            "deleted": deleted,
        },
        session,
        should_set_cookie,
    )


@app.get("/api/settings/backup")
async def export_backup_endpoint(request: Request) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    bundle = export_bundle(session["owner_key"])
    return _session_response(bundle, session, should_set_cookie)


@app.post("/api/settings/restore")
async def restore_backup_endpoint(request: Request, payload: dict[str, Any] = Body(...)) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    try:
        restored = restore_bundle(session["owner_key"], payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _session_response(restored, session, should_set_cookie)


@app.get("/api/runs")
async def list_runs_endpoint(request: Request, limit: int = Query(100, ge=1, le=300)) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    runs = list_runs(session["owner_key"], limit=limit)
    return _session_response({"runs": runs}, session, should_set_cookie)


@app.put("/api/runs/{run_id}")
async def update_run_endpoint(request: Request, run_id: str, payload: dict[str, Any] = Body(...)) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    if payload.get("run_id") != run_id:
        raise HTTPException(status_code=400, detail="run_id mismatch.")

    updated = update_run(session["owner_key"], run_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Run not found.")

    return _session_response({"updated": True, "run_id": run_id}, session, should_set_cookie)


@app.delete("/api/runs")
async def clear_runs_endpoint(request: Request) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    removed = clear_runs(session["owner_key"])
    return _session_response({"deleted_runs": removed}, session, should_set_cookie)


@app.get("/api/providers")
async def providers(request: Request) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    available = _available_providers(session["owner_key"])
    credential_status = list_provider_key_status(session["owner_key"])
    return _session_response(
        {
            "available_providers": available,
            "provider_count": len(available),
            "supported_providers": list(SUPPORTED_PROVIDERS),
            "credential_status": credential_status,
            "defaults": {
                "preset_default": "cinematic-balanced",
                "aspect_ratio": "16:9",
                "duration": 6,
                "variants": 3,
            },
        },
        session,
        should_set_cookie,
    )


@app.get("/api/presets")
async def presets() -> JSONResponse:
    return JSONResponse(
        {
            "presets": [
                {
                    "id": "cinematic-balanced",
                    "name": "Cinematic balanced",
                    "description": "Balanced quality and coherence for most workflows.",
                    "temporal_priority": "high",
                },
                {
                    "id": "coherence-first",
                    "name": "Coherence first",
                    "description": "Prioritizes continuity across outputs.",
                    "temporal_priority": "critical",
                },
                {
                    "id": "speed-first",
                    "name": "Speed first",
                    "description": "Faster turnaround with lower runtime pressure.",
                    "temporal_priority": "medium",
                },
            ]
        }
    )


@app.post("/api/sequences")
async def create_sequence(
    request: Request,
    image: UploadFile = File(...),
    intent: str = Form(...),
    preset: str = Form("cinematic-balanced"),
    duration: float = Form(6.0),
    variants: int = Form(3),
    aspect_ratio: str = Form("16:9"),
    motion_intensity: int = Form(6),
    quality_mode: str = Form("balanced"),
    provider: str = Form("auto"),
    negative_intent: str = Form(""),
) -> JSONResponse:
    session, should_set_cookie = _resolve_session(request)
    owner_key = session["owner_key"]

    intent = intent.strip()
    if not intent:
        raise HTTPException(status_code=400, detail="Intent is required.")

    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="Image file is empty.")

    run_id = f"R{uuid.uuid4().hex[:8]}"
    created_at = _iso_utc()
    variant_count = _parse_variant_count(variants)
    motion_strength = max(0.1, min(motion_intensity / 10.0, 1.0))

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(image.filename or "input.jpg").suffix or ".jpg") as tmp:
        tmp.write(content)
        image_path = Path(tmp.name)

    try:
        try:
            from src.analyzers.movement_predictor import MovementPredictor
            from src.analyzers.scene_analyzer import SceneAnalyzer
        except ModuleNotFoundError as error:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Missing computer-vision dependency for real image analysis. "
                    "Install requirements-cv.txt before running sequence generation."
                ),
            ) from error

        scene_analyzer = SceneAnalyzer(config_path=str(CONFIG_DIR / "scene_analyzer.json"))
        movement_predictor = MovementPredictor(config_path=str(CONFIG_DIR / "movement_prediction_rules.json"))
        prompt_compiler = VideoPromptCompiler(
            catalog_path=str(CONFIG_DIR / "video_prompting_catalog.json"),
            rules_path=str(CONFIG_DIR / "movement_prediction_rules.json"),
        )

        scene_analysis = scene_analyzer.analyze_image(str(image_path))
        movement_analysis = movement_predictor.analyze_image(str(image_path))
        movement_prompt = movement_predictor.get_cinematic_movement_prompt(str(image_path))

        available = _available_providers(owner_key)
        resolved_provider = _resolve_provider(provider, available, preset)
        requested_provider = provider.strip().lower() if provider else "auto"
        pipeline = _build_pipeline(owner_key)

        temporal_priority_map = {
            "coherence-first": "critical",
            "speed-first": "medium",
            "cinematic-balanced": "high",
        }
        temporal_priority = temporal_priority_map.get(preset, "high")

        variants_payload = []
        for index in range(variant_count):
            variant_id = f"{run_id}-v{index + 1}"
            control = VideoControlParameters(
                camera_motion=_variant_camera(index, motion_strength),
                duration_seconds=float(duration),
                fps=24,
                shot_type="medium",
                motion_strength=motion_strength,
            )
            determinism = DeterminismConfig(seed=42, enable_seed_management=True, seed_increment_per_scene=97)

            request_payload = VideoGenerationRequest(
                model_type=_model_type_for_provider(resolved_provider) if resolved_provider else ModelType.RUNWAY,
                scene_description=intent,
                duration=float(duration),
                aspect_ratio=aspect_ratio,
                style="cinematic",
                temporal_consistency_priority=temporal_priority,
                control_parameters=control,
                determinism_config=determinism,
            )
            compiled = prompt_compiler.compile_video_prompt(request_payload, scene_index=index)
            model_parameters = prompt_compiler.compile_model_parameters(compiled)

            execution = None
            status = "not_executed"
            error = None
            used_provider = resolved_provider
            used_model = _model_for_provider(resolved_provider) if resolved_provider else None
            if resolved_provider:
                provider_params = _provider_parameters(
                    provider=resolved_provider,
                    compiled_parameters=model_parameters,
                    duration=float(duration),
                    aspect_ratio=aspect_ratio,
                    quality_mode=quality_mode,
                    motion_intensity=motion_intensity,
                    negative_intent=negative_intent,
                )
                response = pipeline.generate_video(
                    prompt=compiled.prompt_text,
                    provider=_provider_type(resolved_provider),
                    model=used_model,
                    parameters=provider_params,
                    metadata={"run_id": run_id, "variant_id": variant_id},
                )
                execution = response.to_dict()
                if response.is_success():
                    status = "success"
                else:
                    status = "failed"
                    error = response.error.message if response.error else "Provider execution failed."
            else:
                status = "not_configured"
                if requested_provider != "auto" and requested_provider not in available:
                    error = (
                        f"Requested provider '{requested_provider}' is not configured. "
                        "Configure its API key or switch provider to 'auto'."
                    )
                else:
                    error = (
                        "No configured provider API key found. Set RUNWAY_API_KEY, "
                        "PIKA_API_KEY, VEO_API_KEY, SORA_API_KEY/OPENAI_API_KEY, or FLUX_API_KEY."
                    )

            variants_payload.append(
                {
                    "id": variant_id,
                    "label": f"Variant {index + 1}",
                    "status": status,
                    "provider": used_provider,
                    "model": used_model,
                    "prompt_text": compiled.prompt_text,
                    "compiled_prompt": compiled.to_dict(),
                    "model_parameters": model_parameters,
                    "execution": execution,
                    "error": error,
                    "favorite": False,
                }
            )

        if any(variant["status"] == "success" for variant in variants_payload):
            overall_status = "success"
        elif any(variant["status"] == "failed" for variant in variants_payload):
            overall_status = "failed"
        elif any(variant["status"] == "not_configured" for variant in variants_payload):
            overall_status = "not_configured"
        else:
            overall_status = "not_executed"

        payload = {
            "run_id": run_id,
            "created_at": created_at,
            "status": overall_status,
            "intent": intent,
            "preset": preset,
            "params": {
                "duration": duration,
                "variants": variant_count,
                "aspect_ratio": aspect_ratio,
                "motion_intensity": motion_intensity,
                "quality_mode": quality_mode,
                "provider": resolved_provider,
                "provider_requested": requested_provider,
            },
            "source_image": {
                "filename": image.filename,
                "content_type": image.content_type,
                "bytes": len(content),
            },
            "analysis": {
                "scene_type": scene_analysis.get("scene_type", {}),
                "aesthetics": scene_analysis.get("aesthetics", {}),
                "object_count": len(scene_analysis.get("objects", [])),
                "movement_prompt": movement_prompt,
                "movement_prediction_count": len(movement_analysis.get("generated_prompts", [])),
            },
            "available_providers": available,
            "variants": variants_payload,
        }

        save_run(owner_key, payload)

        response = JSONResponse(_json_safe(payload))
        if should_set_cookie:
            _set_session_cookie(response, session["session_id"])
        return response
    finally:
        try:
            image_path.unlink(missing_ok=True)
        except Exception:
            pass
