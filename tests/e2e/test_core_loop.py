"""E2E smoke test for the ANIMAtiZE web console core loop.

Boots the real FastAPI app under uvicorn in a subprocess, drives it with
Playwright (Chromium), and verifies the guest onboarding path:
open page -> Continue as guest -> Try with sample frame -> the generate
button becomes enabled.

Skipped automatically when Playwright or the sandbox Chromium binary
(/opt/pw-browsers/chromium) is unavailable. Do NOT run `playwright install`
in this environment; the browser is preprovisioned.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

CHROMIUM_EXECUTABLE = "/opt/pw-browsers/chromium"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from playwright.sync_api import sync_playwright  # noqa: F401

    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

pytestmark = pytest.mark.skipif(
    not HAS_PLAYWRIGHT or not os.path.exists(CHROMIUM_EXECUTABLE),
    reason=(
        "Playwright (pip install playwright) or the preprovisioned Chromium "
        f"binary at {CHROMIUM_EXECUTABLE} is not available"
    ),
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def server_url(tmp_path_factory: pytest.TempPathFactory):
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["ANIMATIZE_WEB_DB_PATH"] = str(
        tmp_path_factory.mktemp("e2e-web") / "animatize-e2e.db"
    )
    for key in [
        "RUNWAY_API_KEY",
        "PIKA_API_KEY",
        "VEO_API_KEY",
        "SORA_API_KEY",
        "OPENAI_API_KEY",
        "FLUX_API_KEY",
    ]:
        env.pop(key, None)

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.web.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        deadline = time.time() + 30
        while True:
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                pytest.fail(f"uvicorn exited early ({process.returncode}):\n{output}")
            try:
                with urllib.request.urlopen(f"{base_url}/health", timeout=1) as resp:
                    if resp.status == 200:
                        break
            except (urllib.error.URLError, ConnectionError, OSError):
                pass
            if time.time() > deadline:
                process.terminate()
                pytest.fail("uvicorn did not become healthy within 30s")
            time.sleep(0.25)

        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def test_guest_sample_frame_enables_generate(server_url: str):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=CHROMIUM_EXECUTABLE,
            headless=True,
        )
        try:
            page = browser.new_page()
            page.goto(f"{server_url}/", wait_until="load")

            page.get_by_text("Continue as guest").first.click()
            page.get_by_text("Try with sample frame").first.click()

            page.wait_for_function(
                "() => { const b = document.getElementById('generateButton');"
                " return Boolean(b) && !b.disabled; }",
                timeout=15_000,
            )

            generate_disabled = page.eval_on_selector(
                "#generateButton", "(el) => el.disabled"
            )
            assert generate_disabled is False
        finally:
            browser.close()
