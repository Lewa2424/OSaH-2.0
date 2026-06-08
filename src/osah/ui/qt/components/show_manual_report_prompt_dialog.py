from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from osah.ui.qt.design.tokens import COLOR, SPACING


class _ManualReportPromptDialog(QDialog):
    """Компактний діалог нагадування про щоденний звіт.
    Compact daily report reminder dialog.
    """

    _RESULT_BUILD = "build"
    _RESULT_SKIP = "skip"
    _RESULT_LATER = "later"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result = self._RESULT_LATER

        self.setWindowTitle("Щоденний звіт")
        self.setModal(True)
        self.setFixedWidth(380)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        root.setSpacing(SPACING["md"])

        root.addWidget(self._build_message_row())

        self._build_button = QPushButton("Так, сформувати")
        self._build_button.setProperty("variant", "accent")
        self._build_button.setDefault(True)
        self._build_button.clicked.connect(self._accept_build)
        root.addWidget(self._build_button)

        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(SPACING["sm"])

        self._skip_button = QPushButton("Пропустити сьогодні")
        self._skip_button.setProperty("variant", "secondary")
        self._skip_button.clicked.connect(self._accept_skip)
        secondary_row.addWidget(self._skip_button)

        self._later_button = QPushButton("Нагадати пізніше")
        self._later_button.setProperty("variant", "secondary")
        self._later_button.clicked.connect(self._accept_later)
        secondary_row.addWidget(self._later_button)

        root.addLayout(secondary_row)

    def _build_message_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])

        icon_label = QLabel()
        icon_label.setPixmap(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion).pixmap(32, 32)
        )
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(icon_label)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(SPACING["xs"])

        title = QLabel("Настав час сформувати щоденний звіт.")
        title.setWordWrap(True)
        title_font = QFont(title.font())
        title_font.setBold(True)
        title_font.setPixelSize(14)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        text_column.addWidget(title)

        question = QLabel("Сформувати файл звіту зараз?")
        question.setWordWrap(True)
        question.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 13px;")
        text_column.addWidget(question)

        layout.addLayout(text_column, stretch=1)
        return row

    def result_choice(self) -> str:
        return self._result

    def _accept_build(self) -> None:
        self._result = self._RESULT_BUILD
        self.accept()

    def _accept_skip(self) -> None:
        self._result = self._RESULT_SKIP
        self.accept()

    def _accept_later(self) -> None:
        self._result = self._RESULT_LATER
        self.accept()


# ###### ДІАЛОГ НАГАДУВАННЯ ПРО ЩОДЕННИЙ ЗВІТ / SHOW MANUAL REPORT PROMPT DIALOG ######
def show_manual_report_prompt_dialog(parent: QWidget | None) -> str:
    """Показує стилізований діалог нагадування про щоденний звіт і повертає вибір користувача.
    Shows a styled daily report reminder dialog and returns the user's choice.
    """

    dialog = _ManualReportPromptDialog(parent)
    dialog.exec()
    return dialog.result_choice()
