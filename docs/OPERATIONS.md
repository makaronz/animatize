# Operations and troubleshooting (as-built)

This guide covers runtime operations for the active app in `src/web/app.py`.

## Start and stop

Start locally:

```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

If you prefer the launcher:

```bash
python -m src.main
```

Stop with `Ctrl+C`.

## Health and smoke checks

Run these checks after startup:

```bash
curl -sS http://localhost:8000/health
curl -I http://localhost:8000/
```

Expected:

- `/health` returns HTTP `200` and `"status":"ok"`,
- `/` returns HTTP `200`.

## Real generation request check

Use an actual image file:

```bash
curl -sS -X POST "http://localhost:8000/api/sequences" \
  -F "image=@/absolute/path/to/your-image.jpg" \
  -F "intent=Slow cinematic push-in on subject with stable identity" \
  -F "provider=auto"
```

If providers are configured, variants can execute and return provider payloads.
If providers are not configured, response status is explicit
(`not_configured`/`not_executed`) and includes guidance.

## Logging

For local operation, use Uvicorn logs in terminal output.

For higher verbosity:

```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## Common issues

## Error: missing CV dependencies

Symptom:

- `POST /api/sequences` returns `503` with message about CV dependencies.

Fix:

```bash
pip install -r requirements-cv.txt
```

## Provider not executing

Symptom:

- top-level or variant status is `not_configured` or `not_executed`.

Checks:

1. Verify at least one provider key is set in environment.
2. Call `GET /api/providers` and check `available_providers`.
3. If selecting a specific provider in UI, ensure that provider appears in
   `available_providers`.

Example:

```bash
export RUNWAY_API_KEY="..."
curl -sS http://localhost:8000/api/providers
```

## Request returns `failed`

Symptom:

- variant status is `failed`.

Checks:

1. Inspect `variants[].error` in API response.
2. Validate provider account quota and key permissions.
3. Re-run with same image and reduced variant count to isolate.

## Security and secrets

Use these rules in all environments:

1. Keep provider API keys in environment variables only.
2. Do not commit `.env` files with real secrets.
3. Use `.env.example` for documented key names only.
4. Rotate keys if exposure is suspected.

Relevant key names:

- `RUNWAY_API_KEY`
- `PIKA_API_KEY`
- `VEO_API_KEY`
- `SORA_API_KEY` or `OPENAI_API_KEY`
- `FLUX_API_KEY`

## Legacy module note

`src/web/api.py` is a deprecated compatibility surface.
It is not the runtime source of truth and does not provide generation mocks.
