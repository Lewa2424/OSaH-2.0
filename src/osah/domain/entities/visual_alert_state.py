from dataclasses import dataclass

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_level import NotificationLevel


@dataclass(slots=True)
class VisualAlertState:
    """Візуальний стан сигналізації для desktop-shell.
    Визуальное состояние сигнализации для desktop-shell.
    """

    section_levels: dict[AppSection, NotificationLevel]
    should_shake: bool
