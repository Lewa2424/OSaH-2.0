from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class ReissueWorkPermitDialog(QDialog):
    """Модальне вікно причини перевипуску наряду-допуску.
    Modal dialog for entering the work-permit reissue reason.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Перевипустити наряд")
        self.setModal(True)
        self.resize(460, 220)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        hint = QLabel("Вкажіть, чому поточний наряд потрібно перевипустити як новий запис.")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._reason_input = QTextEdit()
        self._reason_input.setMaximumHeight(88)
        self._reason_input.setPlaceholderText("Наприклад: змінено місце виконання або вид робіт.")
        layout.addWidget(self._reason_input)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Скасувати")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        save_button = QPushButton("Перевипустити")
        save_button.setProperty("variant", "accent")
        save_button.clicked.connect(self._accept_if_valid)
        buttons_row.addWidget(save_button)
        layout.addLayout(buttons_row)

    def reissue_reason_text(self) -> str:
        """Повертає введену причину перевипуску.
        Returns the entered reissue reason.
        """

        return self._reason_input.toPlainText().strip()

    def _accept_if_valid(self) -> None:
        """Перевіряє, що причина перевипуску вказана.
        Validates that the reissue reason is provided.
        """

        if not self.reissue_reason_text():
            self._feedback_label.show_error("Потрібно вказати причину перевипуску наряду.")
            return
        self.accept()
