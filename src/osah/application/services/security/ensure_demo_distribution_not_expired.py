from pathlib import Path

from osah.application.services.security.load_demo_distribution_state import load_demo_distribution_state


_DEMO_EXPIRED_MESSAGE = (
    "Термін демонстраційної версії ClearWork завершено. "
    "Для робочої експлуатації зверніться до розробника за повною версією програми."
)


# ###### ПЕРЕВІРКА НЕЗАВЕРШЕНОСТІ DEMO / ENSURE DEMO NOT EXPIRED ######
def ensure_demo_distribution_not_expired(database_path: Path) -> None:
    """Забороняє операцію після завершення 48-годинного demo-only періоду.
    Blocks an operation after the 48-hour demo-only period has ended.
    """

    demo_state = load_demo_distribution_state(database_path)
    if demo_state.is_active and demo_state.is_expired:
        raise ValueError(_DEMO_EXPIRED_MESSAGE)
