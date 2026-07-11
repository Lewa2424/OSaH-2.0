from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class CancelWorkPermitDialog(QDialog):
    """Dialog for canceling a work permit with a required reason. / Діалог скасування наряду."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Скасувати наряд")
        self.setModal(True)
        self.resize(520, 280)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["md"])

        layout.addWidget(QLabel("Вкажіть причину скасування поточного наряду."))

        self._reason_input = QTextEdit()
        self._reason_input.setMinimumHeight(120)
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
        return self._reason_input.toPlainText().strip()

    def _accept_if_valid(self) -> None:
        if not self.reason_text():
            self._feedback_label.show_error("Потрібно вказати причину скасування наряду.")
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
    QTextEdit {{
        background: #FFFFFF;
        border: 1px solid #CBD6E2;
        border-radius: {RADIUS['lg']}px;
        padding: 10px 12px;
        font-size: 14px;
        font-weight: 600;
    }}
    QPushButton {{
        min-height: 40px;
        padding: 0 18px;
        border-radius: {RADIUS['lg']}px;
        font-size: 14px;
        font-weight: 800;
    }}
    """
