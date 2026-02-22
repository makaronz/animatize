#!/usr/bin/env python3
"""
ANIMAtiZE runtime launcher.

Canonical entrypoint is still:
    uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    """Start the canonical FastAPI app from src.web.app."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("ANIMATIZE_RELOAD", "false").lower() == "true"
    uvicorn.run("src.web.app:app", host=host, port=port, reload=reload_enabled)


if __name__ == "__main__":
    main()
