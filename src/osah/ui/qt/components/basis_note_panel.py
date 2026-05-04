from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLineEdit, QTextEdit, QToolButton, QVBoxLayout, QWidget


class BasisNotePanel(QWidget):
    """Згортаний блок підстави та примітки для робочих розділів.
    Collapsible basis-and-note block for operational sections.
    """

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._toggle_button = QToolButton()
        self._toggle_button.setText("▸ Підстава / примітка")
        self._toggle_button.setCheckable(True)
        self._toggle_button.setChecked(False)
        self._toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self._toggle_button.toggled.connect(self._toggle_body)
        layout.addWidget(self._toggle_button)

        self._body = QWidget()
        self._body_layout = QFormLayout(self._body)
        self.basis_text_input = QLineEdit()
        self.basis_note_input = QTextEdit()
        self.basis_note_input.setMaximumHeight(90)
        self._body_layout.addRow("Підстава", self.basis_text_input)
        self._body_layout.addRow("Коментар", self.basis_note_input)
        self._body.setVisible(False)
        layout.addWidget(self._body)

    def set_values(self, basis_text: str, basis_note: str) -> None:
        """Установлює значення полів підстави та примітки.
        Sets basis and note field values.
        """

        self.basis_text_input.setText(basis_text)
        self.basis_note_input.setPlainText(basis_note)
        should_expand = bool(basis_text.strip() or basis_note.strip())
        self._toggle_button.setChecked(should_expand)
        self._toggle_body(should_expand)

    def values(self) -> tuple[str, str]:
        """Повертає поточні значення підстави та примітки.
        Returns current basis and note values.
        """

        return self.basis_text_input.text(), self.basis_note_input.toPlainText()

    def clear(self) -> None:
        """Очищає панель підстави та примітки.
        Clears the basis-and-note panel.
        """

        self.basis_text_input.clear()
        self.basis_note_input.clear()
        self._toggle_button.setChecked(False)
        self._toggle_body(False)

    def _toggle_body(self, checked: bool) -> None:
        self._toggle_button.setText("▾ Підстава / примітка" if checked else "▸ Підстава / примітка")
        self._body.setVisible(checked)
