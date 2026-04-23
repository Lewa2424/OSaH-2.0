from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from osah.domain.entities.medical_status import MedicalStatus
from osah.ui.qt.design.tokens import COLOR


class MedicalStatusBadge(QLabel):
    """Medical admission status badge with text and color."""

    def __init__(self, status: MedicalStatus, text: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(24)
        self.setStyleSheet(_build_badge_style(status))


def _build_badge_style(status: MedicalStatus) -> str:
    """###### СТИЛЬ МЕДБЕЙДЖА / MEDICAL BADGE STYLE ######"""

    palette = {
        MedicalStatus.CURRENT: (COLOR["success_subtle"], COLOR["success"]),
        MedicalStatus.WARNING: (COLOR["warning_subtle"], COLOR["warning"]),
        MedicalStatus.RESTRICTED: (COLOR["restricted_subtle"], COLOR["restricted"]),
        MedicalStatus.EXPIRED: (COLOR["critical_subtle"], COLOR["critical"]),
        MedicalStatus.NOT_FIT: (COLOR["critical_subtle"], COLOR["critical"]),
    }
    background, foreground = palette[status]
    return (
        f"background: {background}; color: {foreground}; border: 1px solid {foreground};"
        "border-radius: 12px; padding: 3px 10px; font-size: 10px; font-weight: 800;"
    )
