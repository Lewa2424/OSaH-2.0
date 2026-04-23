from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from osah.domain.entities.news_source import NewsSource
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class NewsSourcesSettingsPanel(SettingsSectionCard):
    """Trusted news sources section for Settings screen."""

    source_created = Signal(str, str, str)
    source_toggled = Signal(int, bool)

    def __init__(self, sources: tuple[NewsSource, ...], read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only
        self._sources = sources
        layout = self.content_layout()

        title = QLabel("НПА / новини")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        add_row = QHBoxLayout()
        self._name = QLineEdit()
        self._name.setPlaceholderText("Назва джерела")
        add_row.addWidget(self._name)
        self._url = QLineEdit()
        self._url.setPlaceholderText("https://...")
        add_row.addWidget(self._url, stretch=2)
        self._kind = QComboBox()
        self._kind.addItem("НПА", NewsSourceKind.NPA.value)
        self._kind.addItem("Новини", NewsSourceKind.NEWS.value)
        add_row.addWidget(self._kind)
        self._add_button = QPushButton("Додати")
        self._add_button.setProperty("variant", "secondary")
        self._add_button.clicked.connect(self._emit_create)
        add_row.addWidget(self._add_button)
        layout.addLayout(add_row)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Джерело", "Тип", "Активно", "Остання перевірка"])
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)
        self._render_sources()
        self._apply_read_only()

    # ###### ПОБУДОВА ТАБЛИЦІ ДЖЕРЕЛ / RENDER SOURCES TABLE ######
    def _render_sources(self) -> None:
        """Renders trusted sources table with active controls."""

        self._table.setRowCount(0)
        for row_index, source in enumerate(self._sources):
            self._table.insertRow(row_index)
            self._table.setItem(row_index, 0, QTableWidgetItem(source.source_name))
            self._table.setItem(row_index, 1, QTableWidgetItem(source.source_kind.value))

            active_checkbox = QCheckBox()
            active_checkbox.setChecked(source.is_active)
            active_checkbox.setEnabled(not self._read_only)
            active_checkbox.stateChanged.connect(
                lambda _state, source_id=source.source_id, widget=active_checkbox: self.source_toggled.emit(
                    source_id, widget.isChecked()
                )
            )
            self._table.setCellWidget(row_index, 2, active_checkbox)

            last_checked = source.last_checked_at_text or "ще не перевірялось"
            self._table.setItem(row_index, 3, QTableWidgetItem(last_checked))

    # ###### РЕЖИМ READ-ONLY / READ-ONLY MODE ######
    def _apply_read_only(self) -> None:
        """Applies read-only restrictions for manager role."""

        for widget in (self._name, self._url, self._kind, self._add_button):
            widget.setEnabled(not self._read_only)

    # ###### СТВОРЕННЯ ДЖЕРЕЛА / CREATE SOURCE ######
    def _emit_create(self) -> None:
        """Emits request to create new trusted source."""

        self.source_created.emit(
            self._name.text().strip(),
            self._url.text().strip(),
            str(self._kind.currentData() or NewsSourceKind.NEWS.value),
        )
