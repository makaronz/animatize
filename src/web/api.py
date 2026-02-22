"""
Legacy API compatibility module.

This module is intentionally minimal and does not return simulated generation
results. The canonical runtime app is `src.web.app:app`.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


app = FastAPI(
    title="ANIMAtiZE Legacy API",
    description="Deprecated compatibility surface. Use src.web.app endpoints.",
    version="1.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        {
            "status": "deprecated",
            "message": "Legacy API module. Use src.web.app:app as the runtime entrypoint.",
            "canonical_routes": [
                "/",
                "/health",
                "/api/providers",
                "/api/presets",
                "/api/sequences",
            ],
        }
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(
        {
            "status": "deprecated",
            "module": "src.web.api",
            "canonical_module": "src.web.app",
        }
    )


@app.get("/metrics")
async def metrics() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={
            "status": "not_implemented",
            "message": (
                "Metrics are not exposed by src.web.api. "
                "Run src.web.app and integrate real telemetry before enabling this route."
            ),
        },
    )


@app.post("/analyze")
async def analyze_image() -> JSONResponse:
    return JSONResponse(
        status_code=410,
        content={
            "status": "deprecated",
            "message": "This endpoint has been removed. Use POST /api/sequences on src.web.app.",
            "next_step": "Run: uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload",
        },
    )
