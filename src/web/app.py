from __future__ import annotations

import asyncio
import json
import math
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Any, Callable

from fastapi import Body, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
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


# Static provider capability/cost metadata for the frontend provider picker
# ("Camera Cards", docs/UI_UX_AUDIT_REPORT.md section 2.2). Pricing and wait
# estimates are not part of the adapter contracts, and capability values are
# mirrored from each adapter's get_capabilities() so we never have to
# instantiate adapters (which require real API keys) just to describe them.
PROVIDER_METADATA: dict[str, dict[str, Any]] = {
    "sora": {
        "label": "Sora",
        "est_cost_per_second": 0.30,
        "est_wait_seconds": 90,
        "lifecycle": {"status": "deprecated", "note": "API EOL 2026-09-24"},
        "max_duration": 60.0,
        "supports_audio": True,
        "features": {
            "text_to_video": True,
            "image_to_video": True,
            "video_extension": True,
            "prompt_enhancement": True,
            "style_transfer": True,
        },
    },
    "veo": {
        "label": "Veo",
        "est_cost_per_second": 0.35,
        "est_wait_seconds": 40,
        "lifecycle": {"status": "active", "note": None},
        "max_duration": 120.0,
        "supports_audio": True,
        "features": {
            "text_to_video": True,
            "image_to_video": True,
            "video_extension": True,
            "camera_control": True,
            "motion_control": True,
        },
    },
    "runway": {
        "label": "Runway",
        "est_cost_per_second": 0.25,
        "est_wait_seconds": 50,
        "lifecycle": {"status": "migration_recommended", "note": "Gen-3 Alpha EOL 2026-07-30"},
        "max_duration": 16.0,
        "supports_audio": False,
        "features": {
            "text_to_video": True,
            "image_to_video": True,
            "video_to_video": True,
            "motion_brush": True,
            "frame_interpolation": True,
            "upscaling": True,
        },
    },
    "kling": {
        "label": "Kling",
        "est_cost_per_second": 0.15,
        "est_wait_seconds": 60,
        "lifecycle": {"status": "active", "note": None},
        "max_duration": 10.0,
        "supports_audio": True,
        "features": {
            "text_to_video": True,
            "image_to_video": True,
        },
    },
    "luma": {
        "label": "Luma",
        "est_cost_per_second": 0.32,
        "est_wait_seconds": 55,
        "lifecycle": {"status": "active", "note": None},
        "max_duration": 10.0,
        "supports_audio": False,
        "features": {
            "text_to_video": True,
            "image_to_video": True,
        },
    },
    "pika": {
        "label": "Pika",
        "est_cost_per_second": 0.20,
        "est_wait_seconds": 45,
        "lifecycle": {"status": "active", "note": None},
        "max_duration": 10.0,
        "supports_audio": True,
        "features": {
            "text_to_video": True,
            "image_to_video": True,
            "lip_sync": True,
            "sound_effects": True,
            "extend_video": True,
            "modify_region": True,
        },
    },
    "wan": {
        "label": "Wan",
        "est_cost_per_second": 0.10,
        "est_wait_seconds": 70,
        "lifecycle": {"status": "active", "note": None},
        "max_duration": 10.0,
        "supports_audio": False,
        "features": {
            "text_to_video": True,
            "image_to_video": True,
        },
    },
    "flux": {
        "label": "Flux",
        "est_cost_per_second": 0.05,
        "est_wait_seconds": 20,
        "lifecycle": {"status": "active", "note": None},
        "max_duration": None,
        "supports_audio": False,
        "features": {
            "text_to_image": True,
            "image_to_image": True,
            "inpainting": True,
            "controlnet": True,
            "lora": True,
        },
    },
}


def _provider_catalog(available: list[str]) -> list[dict[str, Any]]:
    """Build enriched provider entries for the frontend provider picker."""
    supported = set(SUPPORTED_PROVIDERS)
    catalog = []
    for provider, meta in PROVIDER_METADATA.items():
        catalog.append(
            {
                "id": provider,
                "label": meta["label"],
                "supported": provider in supported,
                "configured": provider in available,
                "est_cost_per_second": meta["est_cost_per_second"],
                "est_wait_seconds": meta["est_wait_seconds"],
                "lifecycle": dict(meta["lifecycle"]),
                "max_duration": meta["max_duration"],
                "supports_audio": meta["supports_audio"],
                "features": dict(meta["features"]),
            }
        )
    return catalog


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


class SequenceCancelled(Exception):
    """Raised inside a background run when the director requested cancellation."""


class SequenceJob:
    """In-memory state for one async sequence run: stage history, terminal event,
    cancel flag, and live SSE subscribers."""

    def __init__(self, run_id: str, loop: asyncio.AbstractEventLoop) -> None:
        self.run_id = run_id
        self.loop = loop
        self.cancel_requested = False
        self.stage_events: list[tuple[str, Any]] = []
        self.terminal_event: tuple[str, Any] | None = None
        self._subscribers: list[asyncio.Queue] = []
        self._lock = threading.Lock()

    @property
    def finished(self) -> bool:
        return self.terminal_event is not None

    def broadcast(self, name: str, data: Any) -> None:
        """Record an event and fan it out to live subscribers.

        Safe to call from the event loop or a worker thread. Events published
        after the terminal event are dropped.
        """
        with self._lock:
            if self.terminal_event is not None:
                return
            if name == "stage":
                self.stage_events.append((name, data))
            else:
                self.terminal_event = (name, data)
            queues = list(self._subscribers)
        for queue in queues:
            self.loop.call_soon_threadsafe(queue.put_nowait, (name, data))

    def subscribe(self) -> tuple[asyncio.Queue, list[tuple[str, Any]], tuple[str, Any] | None]:
        """Snapshot history and register a live queue atomically.

        If the job already finished, no queue is registered and the terminal
        event is returned for immediate replay.
        """
        queue: asyncio.Queue = asyncio.Queue()
        with self._lock:
            history = list(self.stage_events)
            terminal = self.terminal_event
            if terminal is None:
                self._subscribers.append(queue)
        return queue, history, terminal

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)


_SEQUENCE_JOBS: dict[str, SequenceJob] = {}
_SEQUENCE_JOBS_MAX = 50


def _register_sequence_job(job: SequenceJob) -> None:
    """Insert a job, evicting the oldest finished jobs beyond the cap."""
    _SEQUENCE_JOBS[job.run_id] = job
    if len(_SEQUENCE_JOBS) <= _SEQUENCE_JOBS_MAX:
        return
    for run_id in list(_SEQUENCE_JOBS):
        if len(_SEQUENCE_JOBS) <= _SEQUENCE_JOBS_MAX:
            break
        if _SEQUENCE_JOBS[run_id].finished:
            del _SEQUENCE_JOBS[run_id]


def _sse_event(name: str, data: Any) -> str:
    return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _run_stage(
    emit: Callable[[str, str, str, float], None],
    check_cancel: Callable[[], None],
    stage: str,
    start_detail: str,
    start_progress: float,
    end_progress: float,
    fn: Callable[[], tuple[Any, str]],
) -> Any:
    """Run one pipeline stage, emitting started/completed (or failed) events."""
    check_cancel()
    emit(stage, "started", start_detail, start_progress)
    try:
        result, end_detail = fn()
    except SequenceCancelled:
        emit(stage, "failed", "Cancelled by director", start_progress)
        raise
    except HTTPException as error:
        emit(stage, "failed", str(error.detail), start_progress)
        raise
    except Exception as error:
        emit(stage, "failed", str(error), start_progress)
        raise
    emit(stage, "completed", end_detail, end_progress)
    return result


def _execute_sequence_run(
    *,
    owner_key: str,
    run_id: str,
    created_at: str,
    content: bytes,
    filename: str | None,
    content_type: str | None,
    intent: str,
    preset: str,
    duration: float,
    variants: int,
    aspect_ratio: str,
    motion_intensity: int,
    quality_mode: str,
    provider: str,
    negative_intent: str,
    emit: Callable[[str, str, str, float], None] | None = None,
    check_cancel: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Execute a full sequence generation run (blocking).

    Shared by the synchronous POST /api/sequences path (no-op callbacks) and
    the async job worker (stage events + cancellation checks). Returns the run
    payload; the finished run is persisted via save_run exactly like before.
    """
    emit = emit or (lambda stage, status, detail, progress: None)
    check_cancel = check_cancel or (lambda: None)

    variant_count = _parse_variant_count(variants)
    motion_strength = max(0.1, min(motion_intensity / 10.0, 1.0))
    requested_provider = provider.strip().lower() if provider else "auto"

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename or "input.jpg").suffix or ".jpg") as tmp:
        tmp.write(content)
        image_path = Path(tmp.name)

    try:
        # Stage 1: scene_analysis — image validation + CV analysis.
        def _scene_analysis_stage() -> tuple[Any, str]:
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
            scene_analysis = scene_analyzer.analyze_image(str(image_path))
            movement_analysis = movement_predictor.analyze_image(str(image_path))
            movement_prompt = movement_predictor.get_cinematic_movement_prompt(str(image_path))
            object_count = len(scene_analysis.get("objects", []))
            return (
                (scene_analysis, movement_analysis, movement_prompt),
                f"Scene analysis complete: {object_count} objects tracked",
            )

        scene_analysis, movement_analysis, movement_prompt = _run_stage(
            emit,
            check_cancel,
            "scene_analysis",
            f"Analyzing {filename or 'source frame'} for composition and movement",
            0.1,
            0.3,
            _scene_analysis_stage,
        )

        # Stage 2: prompt_compile — provider resolution + prompt/preset assembly.
        def _prompt_compile_stage() -> tuple[Any, str]:
            available = _available_providers(owner_key)
            resolved_provider = _resolve_provider(provider, available, preset)
            prompt_compiler = VideoPromptCompiler(
                catalog_path=str(CONFIG_DIR / "video_prompting_catalog.json"),
                rules_path=str(CONFIG_DIR / "movement_prediction_rules.json"),
            )
            temporal_priority_map = {
                "coherence-first": "critical",
                "speed-first": "medium",
                "cinematic-balanced": "high",
            }
            temporal_priority = temporal_priority_map.get(preset, "high")

            compiled_variants = []
            for index in range(variant_count):
                check_cancel()
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
                compiled_variants.append(
                    {
                        "index": index,
                        "compiled": compiled,
                        "model_parameters": model_parameters,
                        "camera": control.camera_motion,
                    }
                )

            lead = compiled_variants[0]["camera"]
            return (
                (available, resolved_provider, compiled_variants),
                f"Compiled {variant_count} variants ({lead.type}-{lead.direction} lead) with preset {preset}",
            )

        available, resolved_provider, compiled_variants = _run_stage(
            emit,
            check_cancel,
            "prompt_compile",
            f"Compiling {variant_count} camera variants with preset {preset}",
            0.35,
            0.5,
            _prompt_compile_stage,
        )

        # Stage 3: render — provider execution loop over the compiled variants.
        def _render_stage() -> tuple[Any, str]:
            pipeline = _build_pipeline(owner_key)
            variants_payload = []
            for entry in compiled_variants:
                check_cancel()
                index = entry["index"]
                compiled = entry["compiled"]
                model_parameters = entry["model_parameters"]
                variant_id = f"{run_id}-v{index + 1}"

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

            success_count = sum(1 for variant in variants_payload if variant["status"] == "success")
            if resolved_provider:
                detail = f"Rendered {success_count}/{variant_count} variants via {resolved_provider}"
            else:
                detail = "No provider configured; variants compiled without execution"
            return variants_payload, detail

        render_detail = (
            f"Rendering {variant_count} variants via {resolved_provider}"
            if resolved_provider
            else f"Skipping provider execution for {variant_count} variants (no provider configured)"
        )
        variants_payload = _run_stage(
            emit,
            check_cancel,
            "render",
            render_detail,
            0.55,
            0.9,
            _render_stage,
        )

        # Stage 4: qc — response assembly + persistence.
        def _qc_stage() -> tuple[Any, str]:
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
                    "filename": filename,
                    "content_type": content_type,
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
            return payload, f"QC complete: run {run_id} saved to Library with status {overall_status}"

        return _run_stage(
            emit,
            check_cancel,
            "qc",
            "Assembling dailies and persisting run",
            0.92,
            1.0,
            _qc_stage,
        )
    finally:
        try:
            image_path.unlink(missing_ok=True)
        except Exception:
            pass


def _run_sequence_job(job: SequenceJob, run_kwargs: dict[str, Any]) -> None:
    """Background worker (runs in a thread off the event loop)."""

    def emit(stage: str, status: str, detail: str, progress: float) -> None:
        job.broadcast(
            "stage",
            {
                "run_id": job.run_id,
                "stage": stage,
                "status": status,
                "detail": detail,
                "progress": round(float(progress), 3),
            },
        )

    def check_cancel() -> None:
        if job.cancel_requested:
            raise SequenceCancelled()

    try:
        check_cancel()
        emit("queued", "completed", "Picked up by generation worker", 0.05)
        payload = _execute_sequence_run(emit=emit, check_cancel=check_cancel, **run_kwargs)
        job.broadcast("done", _json_safe(payload))
    except SequenceCancelled:
        job.broadcast("error", {"message": "Cancelled by director", "code": "cancelled"})
    except HTTPException as error:
        job.broadcast("error", {"message": str(error.detail), "code": f"http_{error.status_code}"})
    except Exception as error:  # noqa: BLE001 — terminal event must always be emitted
        job.broadcast("error", {"message": str(error), "code": "internal_error"})


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
            "providers": _provider_catalog(available),
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
    async_mode: str = Form(""),
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
    run_kwargs: dict[str, Any] = {
        "owner_key": owner_key,
        "run_id": run_id,
        "created_at": created_at,
        "content": content,
        "filename": image.filename,
        "content_type": image.content_type,
        "intent": intent,
        "preset": preset,
        "duration": duration,
        "variants": variants,
        "aspect_ratio": aspect_ratio,
        "motion_intensity": motion_intensity,
        "quality_mode": quality_mode,
        "provider": provider,
        "negative_intent": negative_intent,
    }

    loop = asyncio.get_running_loop()

    if async_mode == "1":
        job = SequenceJob(run_id=run_id, loop=loop)
        _register_sequence_job(job)
        job.broadcast(
            "stage",
            {
                "run_id": run_id,
                "stage": "queued",
                "status": "started",
                "detail": "Queued in the Dailies Room pipeline",
                "progress": 0.0,
            },
        )
        threading.Thread(
            target=_run_sequence_job,
            args=(job, run_kwargs),
            name=f"animatize-run-{run_id}",
            daemon=True,
        ).start()

        response = JSONResponse(
            {"run_id": run_id, "stream_url": f"/api/sequences/{run_id}/events"},
            status_code=202,
        )
        if should_set_cookie:
            _set_session_cookie(response, session["session_id"])
        return response

    payload = await loop.run_in_executor(None, partial(_execute_sequence_run, **run_kwargs))

    response = JSONResponse(_json_safe(payload))
    if should_set_cookie:
        _set_session_cookie(response, session["session_id"])
    return response


@app.get("/api/sequences/{run_id}/events")
async def sequence_events(run_id: str) -> StreamingResponse:
    job = _SEQUENCE_JOBS.get(run_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Run not found.")

    async def stream():
        queue, history, terminal = job.subscribe()
        if terminal is not None:
            # Late subscriber: replay the terminal event and close.
            yield _sse_event(*terminal)
            return
        try:
            for name, data in history:
                yield _sse_event(name, data)
            while True:
                try:
                    name, data = await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield _sse_event(name, data)
                if name in ("done", "error"):
                    return
        finally:
            job.unsubscribe(queue)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/sequences/{run_id}/cancel")
async def cancel_sequence(run_id: str) -> JSONResponse:
    job = _SEQUENCE_JOBS.get(run_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    if job.finished:
        return JSONResponse({"status": "already_finished"})
    job.cancel_requested = True
    return JSONResponse({"status": "cancelling"})
