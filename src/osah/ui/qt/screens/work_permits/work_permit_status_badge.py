from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.ui.qt.design.tokens import COLOR


class WorkPermitStatusBadge(QLabel):
    """Бейдж статусу наряду-допуску.
    Work permit status badge.
    """

    def __init__(self, status: WorkPermitStatus, text: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(24)
        self.setStyleSheet(_build_badge_style(status))


# ###### СТИЛЬ БЕЙДЖА / BADGE STYLE ######
def _build_badge_style(status: WorkPermitStatus) -> str:
    """Повертає QSS для бейджа статусу наряду.
    Returns QSS for a work permit status badge.
    """

    palette = {
        WorkPermitStatus.ACTIVE: (COLOR["success_subtle"], COLOR["success"]),
        WorkPermitStatus.WARNING: (COLOR["warning_subtle"], COLOR["warning"]),
        WorkPermitStatus.EXPIRED: (COLOR["critical_subtle"], COLOR["critical"]),
        WorkPermitStatus.INVALID: (COLOR["critical_subtle"], COLOR["critical"]),
        WorkPermitStatus.CLOSED: (COLOR["bg_panel"], COLOR["text_muted"]),
        WorkPermitStatus.CANCELED: ("#EEF2FF", "#4338CA"),
    }
    background, foreground = palette[status]
    return (
        f"background: {background}; color: {foreground}; border: 1px solid {foreground};"
        "border-radius: 12px; padding: 3px 10px; font-size: 10px; font-weight: 800;"
    )
