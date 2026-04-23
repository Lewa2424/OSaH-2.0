from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import SPACING


class TaskProgressWidget(QWidget):
    """Unified busy/progress state widget for long operations."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["xs"])

        self._label = QLabel("")
        self._label.setProperty("role", "state_loading")
        layout.addWidget(self._label)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        layout.addWidget(self._bar)
        self.hide()

    # ###### ПОКАЗ НЕВИЗНАЧЕНОГО СТАНУ / SHOW INDETERMINATE STATE ######
    def show_indeterminate(self, message_text: str) -> None:
        """Shows busy state when exact progress value is unknown."""

        self._label.setText(message_text)
        self._bar.setRange(0, 0)
        self.show()

    # ###### ПОКАЗ ПРОГРЕСУ / SHOW PROGRESS ######
    def show_progress(self, message_text: str, progress_value: int) -> None:
        """Shows progress value and message for active operation."""

        self._label.setText(message_text)
        self._bar.setRange(0, 100)
        self._bar.setValue(max(0, min(100, progress_value)))
        self.show()

    # ###### ПРИХОВАННЯ СТАНУ / HIDE STATE ######
    def hide_state(self) -> None:
        """Hides progress widget after operation completion."""

        self.hide()
