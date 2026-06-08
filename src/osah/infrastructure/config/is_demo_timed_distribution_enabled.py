import os
from pathlib import Path

from osah.infrastructure.config.application_paths import build_application_paths


_TRUTHY_VALUES: tuple[str, ...] = ("1", "true", "yes", "on")
_DEMO_TIMED_MARKER_FILE_NAME = "ClearWork.demo_timed"
_ENV_FLAG_NAME = "OSAH_ENABLE_DEMO_TIMED"


# ###### МАРКЕР ДЕМО-ДИСТРИБУЦІЇ / DEMO TIMED DISTRIBUTION MARKER ######
def is_demo_timed_distribution_marker_present(project_root: Path | None = None) -> bool:
    """Повертає True, якщо у каталозі програми є маркер demo-only дистрибуції.
    Returns True when the demo-only distribution marker file is present.
    """

    raw_value = os.environ.get(_ENV_FLAG_NAME, "")
    if raw_value.strip().lower() in _TRUTHY_VALUES:
        return True
    root = project_root if project_root is not None else build_application_paths().project_root
    return (root / _DEMO_TIMED_MARKER_FILE_NAME).is_file()


# ###### ФЛАГ DEMO-ДИСТРИБУЦІЇ В БАЗІ / DEMO DISTRIBUTION DB FLAG ######
def is_demo_timed_distribution_enabled_in_settings(app_settings: dict[str, str]) -> bool:
    """Повертає True, якщо в app_settings увімкнено timed demo distribution.
    Returns True when timed demo distribution is enabled in app_settings.
    """

    from osah.application.services.security.security_setting_keys import DEMO_DISTRIBUTION_ENABLED

    return app_settings.get(DEMO_DISTRIBUTION_ENABLED, "0") == "1"
