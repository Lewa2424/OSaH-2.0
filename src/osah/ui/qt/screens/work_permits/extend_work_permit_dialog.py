from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class ExtendWorkPermitDialog(QDialog):
    """Модальне вікно одноразового продовження наряду-допуску.
    Modal dialog for one-time work permit extension.
    """

    def __init__(self, current_ends_at_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Продовжити наряд")
        self.setModal(True)
        self.resize(460, 280)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        current_label = QLabel(f"Поточний строк дії: {current_ends_at_text}")
        current_label.setWordWrap(True)
        layout.addWidget(current_label)

        self._extended_until_input = QLineEdit()
        self._extended_until_input.setPlaceholderText("ДД.ММ.РРРР HH:MM або YYYY-MM-DD HH:MM")
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
        """Повертає введений новий строк завершення наряду.
        Returns the entered new permit end term.
        """

        return self._extended_until_input.text().strip()

    def extension_reason_text(self) -> str:
        """Повертає введену причину продовження.
        Returns the entered extension reason.
        """

        return self._reason_input.toPlainText().strip()

    def _accept_if_valid(self) -> None:
        """Перевіряє обов'язкові поля діалогу перед закриттям.
        Validates required dialog fields before closing.
        """

        if not self.extended_until_text():
            self._feedback_label.show_error("Потрібно вказати нову дату та час завершення.")
            return
        if not self.extension_reason_text():
            self._feedback_label.show_error("Потрібно вказати причину продовження.")
            return
        self.accept()
