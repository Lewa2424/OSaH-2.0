import os


_TRUTHY_VALUES: tuple[str, ...] = ("1", "true", "yes", "on")


# ###### ФЛАГ DEMO-НАПОЛНЕНИЯ / DEMO SEED FLAG ######
def is_demo_seed_enabled() -> bool:
    """Повертає True, якщо для поточного запуску явно дозволено demo-наповнення.
    Returns True when demo seeding is explicitly enabled for the current run.
    """

    raw_value = os.environ.get("OSAH_ENABLE_DEMO_SEED", "")
    return raw_value.strip().lower() in _TRUTHY_VALUES
