from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from osah.domain.entities.ppe_status import PpeStatus
from osah.ui.qt.design.tokens import COLOR


class PpeStatusBadge(QLabel):
    """Бейдж статусу ЗІЗ з текстом і кольором.
    PPE status badge with text and color.
    """

    def __init__(self, status: PpeStatus, text: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(24)
        self.setStyleSheet(_build_badge_style(status))


def _build_badge_style(status: PpeStatus) -> str:
    """Повертає QSS для бейджа статусу ЗІЗ.
    Returns QSS for a PPE status badge.
    """

    palette = {
        PpeStatus.CURRENT: (COLOR["success_subtle"], COLOR["success"]),
        PpeStatus.WARNING: (COLOR["warning_subtle"], COLOR["warning"]),
        PpeStatus.EXPIRED: (COLOR["critical_subtle"], COLOR["critical"]),
        PpeStatus.NOT_ISSUED: (COLOR["critical_subtle"], COLOR["critical"]),
    }
    background, foreground = palette[status]
    return (
        f"background: {background}; color: {foreground}; border: 1px solid {foreground};"
        "border-radius: 12px; padding: 3px 10px; font-size: 10px; font-weight: 800;"
    )
