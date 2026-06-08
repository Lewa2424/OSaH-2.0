from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class DemoDistributionState:
    """Стан демонстраційної дистрибуції з таймером.
    Timed demo distribution state.
    """

    is_active: bool
    is_expired: bool
    started_at: datetime | None
    expires_at: datetime | None
    remaining_seconds: int
