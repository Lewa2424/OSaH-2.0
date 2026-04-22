from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.ui.qt.design.tokens import COLOR


class TrainingStatusBadge(QLabel):
    """Бейдж статусу інструктажу з текстом і кольором.
    Training status badge with text and color.
    """

    def __init__(self, status_filter: TrainingRegistryFilter, text: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(24)
        self.setStyleSheet(_build_badge_style(status_filter))


# ###### СТИЛЬ СТАТУСУ / STATUS STYLE ######
def _build_badge_style(status_filter: TrainingRegistryFilter) -> str:
    """Повертає QSS для бейджа статусу інструктажу.
    Returns QSS for a training status badge.
    """

    palette = {
        TrainingRegistryFilter.CURRENT: (COLOR["success_subtle"], COLOR["success"]),
        TrainingRegistryFilter.WARNING: (COLOR["warning_subtle"], COLOR["warning"]),
        TrainingRegistryFilter.OVERDUE: (COLOR["critical_subtle"], COLOR["critical"]),
        TrainingRegistryFilter.MISSING: (COLOR["critical_subtle"], COLOR["critical"]),
        TrainingRegistryFilter.ALL: (COLOR["bg_panel"], COLOR["text_secondary"]),
    }
    background, foreground = palette[status_filter]
    return (
        f"background: {background}; color: {foreground}; border: 1px solid {foreground};"
        "border-radius: 12px; padding: 3px 10px; font-size: 10px; font-weight: 800;"
    )
