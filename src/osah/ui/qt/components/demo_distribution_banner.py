"""Баннер демонстраційної версії з таймером / Timed demo distribution banner."""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.application.services.security.load_demo_distribution_state import load_demo_distribution_state
from osah.domain.services.format_demo_remaining_duration import format_demo_remaining_duration
from osah.ui.qt.design.tokens import COLOR, SPACING


class DemoDistributionBanner(QFrame):
    """Показує залишок часу demo-only дистрибуції."""

    def __init__(self, database_path) -> None:
        super().__init__()
        self._database_path = database_path
        self.setObjectName("demoDistributionBanner")
        self.setStyleSheet(
            f"QFrame#demoDistributionBanner {{ "
            f"background: {COLOR['warning_subtle']}; "
            f"border-bottom: 1px solid {COLOR['border_soft']}; "
            f"}}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["sm"], SPACING["xl"], SPACING["sm"])
        layout.setSpacing(0)

        self._label = QLabel()
        self._label.setFont(QFont("Segoe UI", 10))
        self._label.setStyleSheet(f"color: {COLOR['text_primary']};")
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

        self._refresh_text()
        self._timer = QTimer(self)
        self._timer.setInterval(60_000)
        self._timer.timeout.connect(self._refresh_text)
        self._timer.start()

    def _refresh_text(self) -> None:
        demo_state = load_demo_distribution_state(self._database_path)
        if not demo_state.is_active or demo_state.is_expired:
            self.hide()
            self._timer.stop()
            return
        remaining_text = format_demo_remaining_duration(demo_state.remaining_seconds)
        self._label.setText(f"Демонстраційна версія ClearWork · залишилось {remaining_text}")
        self.show()
