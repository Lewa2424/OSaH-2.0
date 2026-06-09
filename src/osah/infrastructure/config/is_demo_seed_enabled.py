import os
import sys

from osah.infrastructure.config.application_paths import build_application_paths

_TRUTHY_VALUES: tuple[str, ...] = ("1", "true", "yes", "on")
_DEMO_MARKER_FILE_NAME = "ClearWork.demo"
_ENABLE_ENV_NAME = "OSAH_ENABLE_DEMO_SEED"
_DISABLE_ENV_NAME = "OSAH_DISABLE_DEMO_SEED"


def _is_truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUTHY_VALUES


# ###### ФЛАГ DEMO-НАПОЛНЕНИЯ / DEMO SEED FLAG ######
def is_demo_seed_enabled() -> bool:
    """Повертає True, якщо для поточного запуску дозволено demo-наповнення.
    Returns True when demo seeding is enabled for the current run.
    """

    if _is_truthy_env(_DISABLE_ENV_NAME):
        return False
    if _is_truthy_env(_ENABLE_ENV_NAME):
        return True

    application_paths = build_application_paths()
    if (application_paths.project_root / _DEMO_MARKER_FILE_NAME).is_file():
        return True

    # Запуск з вихідного коду (IDE/термінал) — демо-засів за замовчуванням.
    if not getattr(sys, "frozen", False):
        return True

    return False
