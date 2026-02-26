# ANIMAtiZE

ANIMAtiZE is an intent-first workflow for generating AI video sequences from a
single source image. The current runtime is a FastAPI application serving a
cinematic web console and backend endpoints for scene analysis, prompt
compilation, auth, persistent settings, and provider execution.

This README is the single source of truth for local onboarding and runtime
startup.

## Current runtime scope

- FastAPI app entrypoint: `src.web.app:app`
- UI: `src/web/static/index.html`, `src/web/static/app.js`,
  `src/web/static/styles.css`
- API routes:
  - `GET /`
  - `GET /health`
  - `GET /api/session/bootstrap`
  - `GET /api/auth/config`
  - `GET /api/auth/me`
  - `POST /api/auth/google`
  - `POST /api/auth/logout`
  - `GET /api/settings`
  - `PUT /api/settings`
  - `GET /api/settings/history`
  - `POST /api/settings/history/{history_id}/restore`
  - `GET /api/settings/api-keys`
  - `PUT /api/settings/api-keys/{provider}`
  - `DELETE /api/settings/api-keys/{provider}`
  - `GET /api/settings/backup`
  - `POST /api/settings/restore`
  - `GET /api/runs`
  - `PUT /api/runs/{run_id}`
  - `DELETE /api/runs`
  - `GET /api/providers`
  - `GET /api/presets`
  - `POST /api/sequences`

## Hard rule: no mock or simulated generation data

The UI and backend must not fabricate generated outputs.

If provider integration is not configured:

- backend returns explicit statuses such as `not_configured` or
  `not_executed`,
- response includes a clear configuration message,
- UI renders this state directly without fake results.

## Requirements

### Required

- Python `3.10+` (tested with Python `3.13`)
- `pip`

### Strongly recommended for real image analysis

- OpenCV and CV dependencies from `requirements-cv.txt`

### Optional

- Node.js (only for advanced local work on TypeScript files in `src/models/`)

## Installation

```bash
git clone https://github.com/makaronz/animatize.git
cd animatize

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-cv.txt
```

## Run locally

Use the canonical entrypoint:

```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

Open:

- `http://localhost:8000/` (UI)
- `http://localhost:8000/health` (health)

## Verify runtime

### 1) Health check

```bash
curl -sS http://localhost:8000/health
```

Expected:

- HTTP `200`
- JSON containing `"status": "ok"`

### 2) UI route

```bash
curl -I http://localhost:8000/
```

Expected:

- HTTP `200`

### 3) Real multipart generation request (no fake payload)

Use an actual image file path:

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

Expected:

- HTTP `200`
- JSON with:
  - `run_id`
  - `status`
  - `analysis`
  - `variants[]`

With provider keys configured, variants can return `success` or `failed`.
Without keys, variants return `not_configured`/`not_executed` with a clear
error message.

## Provider configuration

Set provider keys in environment before startup:

- `RUNWAY_API_KEY`
- `PIKA_API_KEY`
- `VEO_API_KEY`
- `SORA_API_KEY` or `OPENAI_API_KEY`
- `FLUX_API_KEY`
- `GOOGLE_CLIENT_ID` (for Google sign-in)
- `ANIMATIZE_SECRET_KEY` (for API-key encryption at rest)

Example:

```bash
export RUNWAY_API_KEY="..."
export OPENAI_API_KEY="..."
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

If no provider is configured:

- the request still performs real CV analysis and prompt compilation,
- execution status is explicitly non-success (`not_configured` or
  `not_executed`),
- no fabricated media URL is returned.

## Project structure (web runtime)

```text
src/web/
├── app.py            # Canonical FastAPI runtime (UI + API)
├── api.py            # Legacy compatibility module (deprecated surface)
├── persistence.py    # SQLite sessions/settings/runs/API-key persistence
└── static/
    ├── index.html    # Director Console UI
    ├── app.js        # UI interactions, auth, autosave, API wiring
    └── styles.css    # Cinematic design system styles
```

## Documentation map

- API details: `docs/API.md`
- Runtime architecture: `docs/ARCHITECTURE.md`
- MVDS design system: `docs/DESIGN_SYSTEM_MVDS.md`
- Operations and troubleshooting: `docs/OPERATIONS.md`
- Persistence migration: `docs/WEB_CONSOLE_PERSISTENCE_MIGRATION.md`

Older documents may exist for historical context. When onboarding or running
the app, use this README and the four docs above.
