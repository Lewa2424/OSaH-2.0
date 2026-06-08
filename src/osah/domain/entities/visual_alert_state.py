from dataclasses import dataclass

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.nav_fill_palette import NavFillPalette
from osah.domain.entities.notification_level import NotificationLevel


@dataclass(slots=True)
class VisualAlertState:
    """Візуальний стан сигналізації для desktop-shell.
    Визуальное состояние сигнализации для desktop-shell.
    """

    section_levels: dict[AppSection, NotificationLevel]
    section_palettes: dict[AppSection, NavFillPalette | None]
    should_shake: bool
