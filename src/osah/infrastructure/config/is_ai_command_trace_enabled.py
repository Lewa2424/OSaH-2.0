import os
import sys
from pathlib import Path

from osah.infrastructure.config.application_paths import build_application_paths

_ENABLE_ENV_NAME = "OSAH_ENABLE_AI_TRACE_LOG"
_DISABLE_ENV_NAME = "OSAH_DISABLE_AI_TRACE_LOG"
_TRACE_LOG_FILE_NAME = "ai_command_trace.log"


def _is_truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def is_ai_command_trace_enabled() -> bool:
    """Повертає True, якщо увімкнено тимчасовий trace-log AI-команд.
    Returns True when the temporary AI command trace log is enabled.
    """

    if _is_truthy_env(_DISABLE_ENV_NAME):
        return False
    if _is_truthy_env(_ENABLE_ENV_NAME):
        return True
    return not getattr(sys, "frozen", False)


def build_ai_command_trace_log_path() -> Path:
    """Повертає шлях до файлу trace-log AI-команд.
    Returns the path to the AI command trace log file.
    """

    return build_application_paths().log_directory / _TRACE_LOG_FILE_NAME