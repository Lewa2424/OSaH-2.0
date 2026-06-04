import os

from osah.infrastructure.config.application_paths import build_application_paths


_TRUTHY_VALUES: tuple[str, ...] = ("1", "true", "yes", "on")
_DEMO_MARKER_FILE_NAME = "ClearWork.demo"


# ###### ФЛАГ DEMO-НАПОЛНЕНИЯ / DEMO SEED FLAG ######
def is_demo_seed_enabled() -> bool:
    """Повертає True, якщо для поточного запуску дозволено demo-наповнення.
    Returns True when demo seeding is enabled for the current run.
    """

    raw_value = os.environ.get("OSAH_ENABLE_DEMO_SEED", "")
    if raw_value.strip().lower() in _TRUTHY_VALUES:
        return True
    application_paths = build_application_paths()
    return (application_paths.project_root / _DEMO_MARKER_FILE_NAME).is_file()
