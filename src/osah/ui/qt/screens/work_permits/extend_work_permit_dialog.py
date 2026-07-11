from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.domain.services.normalize_ui_datetime_text import normalize_ui_datetime_text
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ExtendWorkPermitDialog(QDialog):
    """Modal dialog for one-time work permit extension. / Модальне вікно продовження наряду."""

    def __init__(self, current_ends_at_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Продовжити наряд")
        self.setModal(True)
        self.resize(500, 320)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["md"])

        current_label = QLabel(f"Поточний строк дії: {current_ends_at_text}")
        current_label.setWordWrap(True)
        layout.addWidget(current_label)

        self._extended_until_input = QLineEdit()
        self._extended_until_input.editingFinished.connect(self._normalize_extended_until_text)
        self._extended_until_input.setPlaceholderText("ДД.ММ.РРРР HH:MM")
        layout.addWidget(QLabel("Нова дата та час завершення"))
        layout.addWidget(self._extended_until_input)

        self._reason_input = QTextEdit()
        self._reason_input.setMaximumHeight(88)
        self._reason_input.setPlaceholderText("Коротко вкажіть причину продовження без зміни заходів безпеки.")
        layout.addWidget(QLabel("Причина продовження"))
        layout.addWidget(self._reason_input)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Скасувати")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        save_button = QPushButton("Продовжити")
        save_button.setProperty("variant", "accent")
        save_button.clicked.connect(self._accept_if_valid)
        buttons_row.addWidget(save_button)
        layout.addLayout(buttons_row)

    def extended_until_text(self) -> str:
        return self._extended_until_input.text().strip()

    def extension_reason_text(self) -> str:
        return self._reason_input.toPlainText().strip()

    def _normalize_extended_until_text(self) -> None:
        normalized_text = self.extended_until_text()
        if not normalized_text:
            return
        try:
            self._extended_until_input.setText(normalize_ui_datetime_text(normalized_text))
            self._feedback_label.clear()
        except ValueError as error:
            self._feedback_label.show_error(str(error))

    def _accept_if_valid(self) -> None:
        if not self.extended_until_text():
            self._feedback_label.show_error("Потрібно вказати нову дату та час завершення.")
            return
        try:
            self._extended_until_input.setText(normalize_ui_datetime_text(self.extended_until_text()))
        except ValueError as error:
            self._feedback_label.show_error(str(error))
            return
        if not self.extension_reason_text():
            self._feedback_label.show_error("Потрібно вказати причину продовження.")
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
