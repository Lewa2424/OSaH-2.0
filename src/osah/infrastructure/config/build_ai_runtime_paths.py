from pathlib import Path

from osah.domain.entities.ai_runtime_paths import AiRuntimePaths
from osah.infrastructure.config.application_paths import build_application_paths


_PRIMARY_MODEL_NAME = "qwen2.5-3b-instruct-q4_k_m.gguf"
_FALLBACK_MODEL_NAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
_SERVER_EXECUTABLE_NAME = "llama-server.exe"


def build_ai_runtime_paths(project_root: Path | None = None) -> AiRuntimePaths:
    """Будує шляхи до llama-server і GGUF-моделей.
    Builds paths to llama-server and GGUF model files.
    """

    application_paths = build_application_paths(project_root)
    resolved_root = application_paths.project_root

    bundled_runtime_directory = resolved_root / "runtime" / "ai"
    development_runtime_directory = resolved_root / "data" / "llama-cpp" / "b9652"
    server_executable = _resolve_first_existing_path(
        (
            bundled_runtime_directory / _SERVER_EXECUTABLE_NAME,
            development_runtime_directory / _SERVER_EXECUTABLE_NAME,
        )
    )
    primary_model_path = _resolve_first_existing_path(
        (
            bundled_runtime_directory / "models" / _PRIMARY_MODEL_NAME,
            resolved_root / "data" / "models" / _PRIMARY_MODEL_NAME,
        )
    )
    fallback_model_path = _resolve_optional_existing_path(
        (
            bundled_runtime_directory / "models" / _FALLBACK_MODEL_NAME,
            resolved_root / "data" / "models" / _FALLBACK_MODEL_NAME,
        )
    )

    return AiRuntimePaths(
        server_executable=server_executable,
        primary_model_path=primary_model_path,
        fallback_model_path=fallback_model_path,
        server_log_path=application_paths.log_directory / "llama-server.log",
    )


def resolve_active_ai_model_path(runtime_paths: AiRuntimePaths, *, prefer_fallback: bool = False) -> Path:
    """Повертає активну модель з урахуванням fallback.
    Returns the active model path with optional fallback preference.
    """

    if prefer_fallback and runtime_paths.fallback_model_path is not None:
        return runtime_paths.fallback_model_path
    if runtime_paths.primary_model_path.is_file():
        return runtime_paths.primary_model_path
    if runtime_paths.fallback_model_path is not None and runtime_paths.fallback_model_path.is_file():
        return runtime_paths.fallback_model_path
    return runtime_paths.primary_model_path


def is_ai_runtime_bundle_available(runtime_paths: AiRuntimePaths) -> bool:
    """Перевіряє наявність runtime і хоча б однієї моделі.
    Checks whether runtime binaries and at least one model exist.
    """

    if not runtime_paths.server_executable.is_file():
        return False
    return resolve_active_ai_model_path(runtime_paths).is_file()


def _resolve_first_existing_path(candidates: tuple[Path, ...]) -> Path:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def _resolve_optional_existing_path(candidates: tuple[Path, ...]) -> Path | None:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None
