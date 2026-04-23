from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import SPACING


class EmptyStateWidget(QWidget):
    """Unified empty-state widget."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACING["sm"], 0, 0)
        layout.setSpacing(SPACING["xs"])

        self._title = QLabel("")
        self._title.setProperty("role", "state_title")
        self._subtitle = QLabel("")
        self._subtitle.setProperty("role", "state_subtitle")
        self._subtitle.setWordWrap(True)
        layout.addWidget(self._title)
        layout.addWidget(self._subtitle)
        self.hide()

    # ###### ПОКАЗ ПОРОЖНЬОГО СТАНУ / SHOW EMPTY STATE ######
    def show_state(self, title_text: str, subtitle_text: str = "") -> None:
        """Shows empty-state message."""

        self._title.setText(title_text)
        self._subtitle.setText(subtitle_text)
        self._subtitle.setVisible(bool(subtitle_text.strip()))
        self.show()


class LoadingStateWidget(QWidget):
    """Unified loading-state widget."""

    def __init__(self, message_text: str = "Завантаження даних...") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACING["sm"], 0, 0)
        self._label = QLabel(message_text)
        self._label.setProperty("role", "state_loading")
        layout.addWidget(self._label)
        self.hide()

    # ###### ПОКАЗ СТАНУ ЗАВАНТАЖЕННЯ / SHOW LOADING STATE ######
    def show_state(self, message_text: str = "Завантаження даних...") -> None:
        """Shows loading-state message."""

        self._label.setText(message_text)
        self.show()


class ErrorStateWidget(QWidget):
    """Unified error-state widget."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACING["sm"], 0, 0)
        self._label = QLabel("")
        self._label.setProperty("role", "state_error")
        self._label.setWordWrap(True)
        layout.addWidget(self._label)
        self.hide()

    # ###### ПОКАЗ СТАНУ ПОМИЛКИ / SHOW ERROR STATE ######
    def show_state(self, message_text: str) -> None:
        """Shows error-state message."""

        self._label.setText(message_text)
        self.show()
