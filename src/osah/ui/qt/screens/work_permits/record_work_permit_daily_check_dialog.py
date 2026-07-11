from datetime import datetime

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.domain.services.normalize_ui_datetime_text import normalize_ui_datetime_text
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class RecordWorkPermitDailyCheckDialog(QDialog):
    """Modal dialog for recording a daily work-area check. / Діалог щоденної перевірки."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Щоденна перевірка")
        self.setModal(True)
        self.resize(500, 320)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["md"])

        current_moment_text = datetime.now().strftime("%d.%m.%Y %H:%M")
        self._checked_at_input = QLineEdit(current_moment_text)
        self._checked_at_input.editingFinished.connect(self._normalize_checked_at_text)
        self._checked_at_input.setPlaceholderText("ДД.ММ.РРРР HH:MM")
        layout.addWidget(QLabel("Дата та час перевірки"))
        layout.addWidget(self._checked_at_input)

        self._checked_by_input = QLineEdit()
        self._checked_by_input.setPlaceholderText("Хто виконав перевірку місця робіт")
        layout.addWidget(QLabel("Перевірив"))
        layout.addWidget(self._checked_by_input)

        self._note_input = QTextEdit()
        self._note_input.setMaximumHeight(88)
        self._note_input.setPlaceholderText("За потреби зафіксуйте коротку примітку до щоденної перевірки.")
        layout.addWidget(QLabel("Примітка"))
        layout.addWidget(self._note_input)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Скасувати")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        save_button = QPushButton("Зафіксувати")
        save_button.setProperty("variant", "accent")
        save_button.clicked.connect(self._accept_if_valid)
        buttons_row.addWidget(save_button)
        layout.addLayout(buttons_row)

    def checked_at_text(self) -> str:
        return self._checked_at_input.text().strip()

    def checked_by_text(self) -> str:
        return self._checked_by_input.text().strip()

    def note_text(self) -> str:
        return self._note_input.toPlainText().strip()

    def _normalize_checked_at_text(self) -> None:
        normalized_text = self.checked_at_text()
        if not normalized_text:
            return
        try:
            self._checked_at_input.setText(normalize_ui_datetime_text(normalized_text))
            self._feedback_label.clear()
        except ValueError as error:
            self._feedback_label.show_error(str(error))

    def _accept_if_valid(self) -> None:
        if not self.checked_at_text():
            self._feedback_label.show_error("Потрібно вказати дату та час щоденної перевірки.")
            return
        try:
            self._checked_at_input.setText(normalize_ui_datetime_text(self.checked_at_text()))
        except ValueError as error:
            self._feedback_label.show_error(str(error))
            return
        if not self.checked_by_text():
            self._feedback_label.show_error("Потрібно вказати, хто виконав щоденну перевірку.")
            return
        self.accept()


def _dialog_stylesheet() -> str:
    return f"""
    QDialog {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F8FBFD, stop:1 #EFF4F9);
    }}
    QLabel {{
        color: {COLOR['text_primary']};
        font-size: 14px;
        font-weight: 700;
    }}
    QLineEdit, QTextEdit {{
        background: #FFFFFF;
        border: 1px solid #CBD6E2;
        border-radius: {RADIUS['lg']}px;
        font-size: 14px;
        font-weight: 600;
    }}
    QLineEdit {{
        min-height: 40px;
        padding: 0 14px;
    }}
    QTextEdit {{
        padding: 10px 12px;
    }}
    QPushButton {{
        min-height: 40px;
        padding: 0 18px;
        border-radius: {RADIUS['lg']}px;
        font-size: 14px;
        font-weight: 800;
    }}
    """
