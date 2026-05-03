from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, SPACING


class SectionHeader(QWidget):
    """Unified section header with title and optional subtitle."""

    def __init__(self, title_text: str, subtitle_text: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["xs"])

        title = QLabel(title_text)
        title.setProperty("role", "section_header_title")
        layout.addWidget(title)

        self._subtitle = QLabel(subtitle_text)
        self._subtitle.setProperty("role", "section_header_subtitle")
        self._subtitle.setVisible(bool(subtitle_text.strip()))
        layout.addWidget(self._subtitle)
        self.hide()

    # ###### ОНОВЛЕННЯ ПІДЗАГОЛОВКА / UPDATE SUBTITLE ######
    def set_subtitle(self, subtitle_text: str) -> None:
        """Updates section subtitle and its visibility."""

        self._subtitle.setText(subtitle_text)
        self._subtitle.setVisible(bool(subtitle_text.strip()))

    # ###### АКЦЕНТ ПОПЕРЕДЖЕННЯ / WARNING ACCENT ######
    def set_warning_accent(self, enabled: bool) -> None:
        """Sets warning accent for subtitle when attention is required."""

        if enabled:
            self._subtitle.setStyleSheet(f"color: {COLOR['warning']}; font-weight: 700;")
            return
        self._subtitle.setStyleSheet("")
