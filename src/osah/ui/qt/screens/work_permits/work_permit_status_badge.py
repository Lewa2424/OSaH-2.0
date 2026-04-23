from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.ui.qt.design.tokens import COLOR


class WorkPermitStatusBadge(QLabel):
    """Work permit status badge."""

    def __init__(self, status: WorkPermitStatus, text: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(24)
        self.setStyleSheet(_build_badge_style(status))


def _build_badge_style(status: WorkPermitStatus) -> str:
    """###### СТИЛЬ БЕЙДЖА НД / WORK PERMIT BADGE STYLE ######"""

    palette = {
        WorkPermitStatus.ACTIVE: (COLOR["success_subtle"], COLOR["success"]),
        WorkPermitStatus.WARNING: (COLOR["warning_subtle"], COLOR["warning"]),
        WorkPermitStatus.EXPIRED: (COLOR["critical_subtle"], COLOR["critical"]),
        WorkPermitStatus.INVALID: (COLOR["critical_subtle"], COLOR["critical"]),
        WorkPermitStatus.CLOSED: (COLOR["status_archive_bg"], COLOR["status_archive_text"]),
        WorkPermitStatus.CANCELED: (COLOR["restricted_subtle"], COLOR["restricted"]),
    }
    background, foreground = palette[status]
    return (
        f"background: {background}; color: {foreground}; border: 1px solid {foreground};"
        "border-radius: 12px; padding: 3px 10px; font-size: 10px; font-weight: 800;"
    )
