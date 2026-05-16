from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class CancelWorkPermitDialog(QDialog):
    """Діалог скасування наряду-допуску з обов'язковою причиною.
    Dialog for canceling a work permit with a required reason.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Скасувати наряд")
        self.setModal(True)
        self.resize(520, 260)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        layout.addWidget(QLabel("Вкажіть причину скасування поточного наряду."))

        self._reason_input = QTextEdit()
        self._reason_input.setMinimumHeight(110)
        layout.addWidget(self._reason_input)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Закрити")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        confirm_button = QPushButton("Скасувати наряд")
        confirm_button.setProperty("variant", "accent")
        confirm_button.clicked.connect(self._accept_if_valid)
        buttons_row.addWidget(confirm_button)
        layout.addLayout(buttons_row)

    def reason_text(self) -> str:
        """Повертає нормалізовану причину скасування.
        Returns the normalized cancellation reason.
        """

        return self._reason_input.toPlainText().strip()

    def _accept_if_valid(self) -> None:
        if not self.reason_text():
            self._feedback_label.show_error("Потрібно вказати причину скасування наряду.")
            return
        self.accept()
