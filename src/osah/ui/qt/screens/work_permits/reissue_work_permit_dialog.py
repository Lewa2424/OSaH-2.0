from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ReissueWorkPermitDialog(QDialog):
    """Modal dialog for entering reissue reason. / Діалог причини перевипуску наряду."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Перевипустити наряд")
        self.setModal(True)
        self.resize(480, 240)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["md"])

        hint = QLabel("Вкажіть, чому поточний наряд потрібно перевипустити як новий запис.")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._reason_input = QTextEdit()
        self._reason_input.setMaximumHeight(96)
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
        return self._reason_input.toPlainText().strip()

    def _accept_if_valid(self) -> None:
        if not self.reissue_reason_text():
            self._feedback_label.show_error("Потрібно вказати причину перевипуску наряду.")
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
