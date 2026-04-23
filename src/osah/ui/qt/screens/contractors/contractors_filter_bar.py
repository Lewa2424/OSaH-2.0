from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class ContractorsFilterBar(QWidget):
    """Filters for contractors registry."""

    filters_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Пошук: організація, контакт, телефон, email")
        self._search.textChanged.connect(lambda _text: self.filters_changed.emit())
        layout.addWidget(self._search, stretch=2)

        self._status = QComboBox()
        self._status.addItem("Усі статуси", "")
        self._status.addItem("Активний", "active")
        self._status.addItem("Завершений", "finished")
        self._status.addItem("Архівний", "archived")
        self._status.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self._status)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self._reset)
        layout.addWidget(reset_button)

        self._active_label = QLabel("Фільтри не активні")
        layout.addWidget(self._active_label)

    # ###### СКИДАННЯ ФІЛЬТРІВ / RESET FILTERS ######
    def _reset(self) -> None:
        """Resets contractors filters."""

        self._search.clear()
        self._status.setCurrentIndex(0)
        self._update_indicator()
        self.filters_changed.emit()

    # ###### ЧИТАННЯ ЗНАЧЕНЬ ФІЛЬТРІВ / READ FILTER VALUES ######
    def values(self) -> dict[str, str]:
        """Returns current filter values."""

        values = {
            "search": self._search.text().strip().lower(),
            "status": str(self._status.currentData() or ""),
        }
        self._update_indicator()
        return values

    # ###### ІНДИКАТОР АКТИВНИХ ФІЛЬТРІВ / ACTIVE FILTERS INDICATOR ######
    def _update_indicator(self) -> None:
        """Updates active filters indicator label."""

        count = int(bool(self._search.text().strip())) + int(bool(self._status.currentData()))
        self._active_label.setText("Фільтри не активні" if count == 0 else f"Активних фільтрів: {count}")
