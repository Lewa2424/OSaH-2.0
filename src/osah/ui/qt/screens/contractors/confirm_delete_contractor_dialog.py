from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, SPACING


class ConfirmDeleteContractorDialog(QDialog):
    """Діалог підтвердження видалення підрядника.
    Contractor deletion confirmation dialog.
    """

    def __init__(self, contractor_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Видалити підрядника")
        self.setModal(True)
        self.resize(440, 170)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; color: {COLOR['text_primary']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title_label = QLabel("Видалити поточний запис підрядника з реєстру?")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        if contractor_name.strip():
            name_label = QLabel(f"Організація: {contractor_name.strip()}")
            name_label.setStyleSheet(f"color: {COLOR['text_secondary']};")
            name_label.setWordWrap(True)
            layout.addWidget(name_label)

        note_label = QLabel("Дію буде зафіксовано в журналі аудиту.")
        note_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Скасувати")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        confirm_button = QPushButton("Видалити")
        confirm_button.setProperty("variant", "accent")
        confirm_button.clicked.connect(self.accept)
        buttons_row.addWidget(confirm_button)
        layout.addLayout(buttons_row)
