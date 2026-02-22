# API reference (as-built)

This document describes the currently implemented API in
`src/web/app.py`.

The canonical runtime entrypoint is:

```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

## Base URL

- Local: `http://localhost:8000`

## Endpoint summary

1. `GET /`
2. `GET /health`
3. `GET /api/providers`
4. `GET /api/presets`
5. `POST /api/sequences`

## `GET /`

Serves the V1 UI page from `src/web/static/index.html`.

### Response

- `200` with HTML body.

## `GET /health`

Liveness endpoint for runtime checks.

### Response

- `200` JSON:

```json
{
  "status": "ok",
  "timestamp": "2026-02-22T10:11:12.123456+00:00"
}
```

## `GET /api/providers`

Returns currently configured provider capability based on environment keys.

### Response

- `200` JSON:

```json
{
  "available_providers": ["runway", "sora"],
  "provider_count": 2,
  "defaults": {
    "preset_default": "cinematic-balanced",
    "aspect_ratio": "16:9",
    "duration": 6,
    "variants": 3
  }
}
```

## `GET /api/presets`

Returns built-in generation presets.

### Response

- `200` JSON:

```json
{
  "presets": [
    {
      "id": "cinematic-balanced",
      "name": "Cinematic balanced",
      "description": "Balanced quality and coherence for most workflows.",
      "temporal_priority": "high"
    },
    {
      "id": "coherence-first",
      "name": "Coherence first",
      "description": "Prioritizes continuity across outputs.",
      "temporal_priority": "critical"
    },
    {
      "id": "speed-first",
      "name": "Speed first",
      "description": "Faster turnaround with lower runtime pressure.",
      "temporal_priority": "medium"
    }
  ]
}
```

## `POST /api/sequences`

Creates a sequence request from image + intent and executes the real pipeline:

1. scene analysis (`SceneAnalyzer`),
2. movement analysis (`MovementPredictor`),
3. prompt compilation (`VideoPromptCompiler`),
4. provider execution (`VideoGenerationPipeline`) when configured.

### Content type

- `multipart/form-data`

### Form fields

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `image` | file | yes | - | Real image payload |
| `intent` | string | yes | - | Non-empty |
| `preset` | string | no | `cinematic-balanced` | `cinematic-balanced`, `coherence-first`, `speed-first` |
| `duration` | float | no | `6.0` | seconds |
| `variants` | int | no | `3` | clamped to `2..5` |
| `aspect_ratio` | string | no | `16:9` | `16:9`, `9:16`, `1:1`, `4:5` |
| `motion_intensity` | int | no | `6` | interpreted into motion strength |
| `quality_mode` | string | no | `balanced` | `fast`, `balanced`, `high` |
| `provider` | string | no | `auto` | specific provider or `auto` |
| `negative_intent` | string | no | empty | optional negative prompt |

### Curl example (real upload)

```bash
curl -sS -X POST "http://localhost:8000/api/sequences" \
  -F "image=@/absolute/path/to/your-image.jpg" \
  -F "intent=Slow cinematic push-in on subject with stable identity" \
  -F "preset=cinematic-balanced" \
  -F "duration=6" \
  -F "variants=3" \
  -F "aspect_ratio=16:9" \
  -F "motion_intensity=6" \
  -F "quality_mode=balanced" \
  -F "provider=auto" \
  -F "negative_intent=avoid jitter and identity drift"
```

### Response shape

- `200` JSON with:
  - run metadata: `run_id`, `created_at`, `status`,
  - request echo: `intent`, `preset`, `params`,
  - source metadata: `source_image`,
  - analysis summary: `analysis`,
  - provider list: `available_providers`,
  - variant list: `variants[]`.

Variant object includes:

- `id`, `label`, `status`, `provider`, `model`,
- `prompt_text`, `compiled_prompt`, `model_parameters`,
- `execution` (provider response when executed),
- `error` (human-readable failure/config message).

## Status semantics

Top-level `status` and variant `status` can be:

- `success`: provider call succeeded.
- `failed`: provider call executed but failed.
- `not_configured`: provider keys missing or selected provider not configured.
- `not_executed`: request processed but execution was not started.

## Error and edge behavior

### Input validation

- empty `intent` -> `400`
- empty file payload -> `400`

### Missing CV dependencies

- if required CV packages are missing -> `503` with explicit message to install
  `requirements-cv.txt`.

### Provider not configured

- request still returns real analysis and compiled prompts,
- execution statuses are non-success (`not_configured` or `not_executed`),
- no fake video URL is fabricated.

## Legacy module note

`src/web/api.py` is a compatibility module and is deprecated.
It does not provide generated mock outputs and is not the canonical runtime.
