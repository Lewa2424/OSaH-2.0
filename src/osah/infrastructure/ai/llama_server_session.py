from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from osah.domain.entities.ai_runtime_paths import AiRuntimePaths
from osah.infrastructure.ai.is_llama_server_healthy import is_llama_server_healthy


_server_process: subprocess.Popen[str] | None = None
_active_runtime_paths: AiRuntimePaths | None = None


def build_llama_server_base_url(runtime_paths: AiRuntimePaths) -> str:
    """Повертає базовий URL локального llama-server.
    Returns the local llama-server base URL.
    """

    return f"http://{runtime_paths.server_host}:{runtime_paths.server_port}"


def ensure_llama_server_running(runtime_paths: AiRuntimePaths, model_path: Path) -> str:
    """Запускає llama-server за потреби і чекає /health.
    Starts llama-server when needed and waits for /health.
    """

    global _server_process, _active_runtime_paths

    base_url = build_llama_server_base_url(runtime_paths)
    if is_llama_server_healthy(base_url):
        return base_url

    if _server_process is not None and _server_process.poll() is None:
        _wait_for_health(base_url, timeout_seconds=90.0)
        if is_llama_server_healthy(base_url):
            return base_url

    if not runtime_paths.server_executable.is_file():
        raise RuntimeError("Не знайдено llama-server.exe.")
    if not model_path.is_file():
        raise RuntimeError(f"Не знайдено модель: {model_path.name}")

    runtime_paths.server_log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = runtime_paths.server_log_path.open("a", encoding="utf-8")
    command = [
        str(runtime_paths.server_executable),
        "-m",
        str(model_path),
        "--host",
        runtime_paths.server_host,
        "--port",
        str(runtime_paths.server_port),
        "-c",
        # Slim prompt + n_ctx 4096: write semantic ~1.2k tok, read ~0.6k; user blocks до ~1k. Бенчмарк: tests/test_ai_runtime_context_budget.py
        "4096",
        "-ngl",
        "0",
        "--threads",
        "4",
    ]
    creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        _server_process = subprocess.Popen(
            command,
            cwd=str(runtime_paths.server_executable.parent),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creation_flags,
        )
    finally:
        log_file.close()
    _active_runtime_paths = runtime_paths
    _wait_for_health(base_url, timeout_seconds=120.0)

    if not is_llama_server_healthy(base_url):
        stop_llama_server_process()
        raise RuntimeError("llama-server не пройшов health-check.")

    return base_url


def stop_llama_server_process() -> None:
    """Зупиняє локальний llama-server, якщо він був запущений застосунком.
    Stops the local llama-server started by the application.
    """

    global _server_process, _active_runtime_paths

    if _server_process is None:
        return

    if _server_process.poll() is None:
        _server_process.terminate()
        try:
            _server_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            _server_process.kill()
            _server_process.wait(timeout=5)

    _server_process = None
    _active_runtime_paths = None


def _wait_for_health(base_url: str, *, timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if is_llama_server_healthy(base_url):
            return
        time.sleep(0.5)
    raise TimeoutError("Час очікування llama-server вичерпано.")
