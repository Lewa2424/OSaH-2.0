from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, SPACING


class CloseWorkPermitDialog(QDialog):
    """Діалог підтвердження ручного закриття наряду-допуску.
    Confirmation dialog for manually closing a work permit.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Закрити наряд")
        self.setModal(True)
        self.resize(440, 180)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        message = QLabel(
            "Підтвердіть ручне закриття наряду-допуску. "
            "Після закриття він перейде в історичний стан і не редагуватиметься."
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
