from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class CloseWorkPermitDialog(QDialog):
    """Confirmation dialog for manually closing a work permit. / Діалог закриття наряду."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Закрити наряд")
        self.setModal(True)
        self.resize(460, 200)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["md"])

        message = QLabel(
            "Підтвердіть ручне закриття наряду-допуску. Після закриття він перейде в історичний стан і не редагуватиметься."
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Скасувати")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        confirm_button = QPushButton("Закрити наряд")
        confirm_button.setProperty("variant", "accent")
        confirm_button.clicked.connect(self.accept)
        buttons_row.addWidget(confirm_button)
        layout.addLayout(buttons_row)


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
    QPushButton {{
        min-height: 40px;
        padding: 0 18px;
        border-radius: {RADIUS['lg']}px;
        font-size: 14px;
        font-weight: 800;
    }}
    """
