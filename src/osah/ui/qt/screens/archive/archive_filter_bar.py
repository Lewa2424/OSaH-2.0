from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from osah.domain.entities.archive_entry_type import ArchiveEntryType


class ArchiveFilterBar(QWidget):
    """Filters for archive registry."""

    filters_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._type_filter = QComboBox()
        self._type_filter.addItem("Усі типи", "")
        self._type_filter.addItem("Архівні працівники", ArchiveEntryType.EMPLOYEE.value)
        self._type_filter.addItem("Історичні наряди", ArchiveEntryType.WORK_PERMIT.value)
        self._type_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self._type_filter)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Пошук: ПІБ, номер, причина, підрозділ")
        self._search.textChanged.connect(lambda _text: self.filters_changed.emit())
        layout.addWidget(self._search, stretch=1)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self._reset_filters)
        layout.addWidget(reset_button)

        self._active_label = QLabel("Фільтри не активні")
        layout.addWidget(self._active_label)

    # ###### СКИДАННЯ ФІЛЬТРІВ / RESET FILTERS ######
    def _reset_filters(self) -> None:
        """Resets archive filters to defaults."""

        self._type_filter.setCurrentIndex(0)
        self._search.clear()
        self._update_indicator()
        self.filters_changed.emit()

    # ###### ЧИТАННЯ СТАНУ ФІЛЬТРІВ / READ FILTER VALUES ######
    def values(self) -> dict[str, str]:
        """Returns current archive filters."""

        values = {
            "entry_type": str(self._type_filter.currentData() or ""),
            "search": self._search.text().strip().lower(),
        }
        self._update_indicator()
        return values

    # ###### ІНДИКАТОР АКТИВНИХ ФІЛЬТРІВ / ACTIVE FILTERS INDICATOR ######
    def _update_indicator(self) -> None:
        """Updates active filters indicator."""

        count = int(bool(self._type_filter.currentData())) + int(bool(self._search.text().strip()))
        self._active_label.setText("Фільтри не активні" if count == 0 else f"Активних фільтрів: {count}")
