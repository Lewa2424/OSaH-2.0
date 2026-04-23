from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.ui.qt.design.tokens import COLOR


class EmployeeRowStateBadge(QLabel):
    """Compact employee status badge for table and card."""

    def __init__(self, level: EmployeeStatusLevel, text: str) -> None:
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(24)
        self.setStyleSheet(_build_badge_stylesheet(level))


def _build_badge_stylesheet(level: EmployeeStatusLevel) -> str:
    """###### СТИЛЬ БЕЙДЖА СТАТУСУ / STATUS BADGE STYLE ######"""

    palette = {
        EmployeeStatusLevel.NORMAL: (COLOR["success_subtle"], COLOR["success"], COLOR["success"]),
        EmployeeStatusLevel.WARNING: (COLOR["warning_subtle"], COLOR["warning"], COLOR["warning"]),
        EmployeeStatusLevel.CRITICAL: (COLOR["critical_subtle"], COLOR["critical"], COLOR["critical"]),
        EmployeeStatusLevel.RESTRICTED: (COLOR["restricted_subtle"], COLOR["restricted_text"], COLOR["restricted"]),
        EmployeeStatusLevel.ARCHIVED: (COLOR["status_archive_bg"], COLOR["status_archive_text"], COLOR["status_archive"]),
    }
    background, foreground, border = palette[level]
    return (
        f"background: {background};"
        f"color: {foreground};"
        f"border: 1px solid {border};"
        "border-radius: 12px;"
        "padding: 3px 10px;"
        "font-size: 10px;"
        "font-weight: 700;"
    )
