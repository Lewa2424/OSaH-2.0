from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QTime

from osah.domain.entities.news_source import NewsSource
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class NewsSourcesSettingsPanel(SettingsSectionCard):
    """Trusted news sources section for Settings screen."""

    source_created = Signal(str, str, str)
    source_toggled = Signal(int, bool)
    sources_deleted = Signal(list)  # list[int] — source_ids
    refresh_now_requested = Signal()
    refresh_time_saved = Signal(str)  # HH:MM

    def __init__(
        self,
        sources: tuple[NewsSource, ...],
        read_only: bool,
        news_refresh_time: str = "09:00",
    ) -> None:
        super().__init__()
        self._read_only = read_only
        self._sources = sources
        self._news_refresh_time = news_refresh_time
        layout = self.content_layout()

        title = QLabel("НПА / новини")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        # ###### РЯДОК ДОДАВАННЯ / ADD ROW ######
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

        # ###### РЯДОК ДІЙ З ТАБЛИЦЕЮ / ACTION ROW ######
        action_row = QHBoxLayout()

        self._refresh_now_button = QPushButton("⟳  Перевірити зараз")
        self._refresh_now_button.setProperty("variant", "secondary")
        self._refresh_now_button.setEnabled(not self._read_only)
        self._refresh_now_button.clicked.connect(self.refresh_now_requested.emit)
        action_row.addWidget(self._refresh_now_button)

        self._schedule_button = QPushButton("🕐  Налаштувати розклад")
        self._schedule_button.setProperty("variant", "secondary")
        self._schedule_button.setEnabled(not self._read_only)
        self._schedule_button.clicked.connect(self._open_schedule_dialog)
        action_row.addWidget(self._schedule_button)

        action_row.addStretch()

        self._delete_button = QPushButton("Видалити обрані")
        self._delete_button.setProperty("variant", "danger")
        self._delete_button.setEnabled(False)
        self._delete_button.clicked.connect(self._emit_delete_selected)
        action_row.addWidget(self._delete_button)

        layout.addLayout(action_row)

        # ###### ТАБЛИЦЯ ДЖЕРЕЛ / SOURCES TABLE ######
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["", "Джерело", "Тип", "Активно", "Остання перевірка"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.itemChanged.connect(self._on_table_item_changed)
        layout.addWidget(ScrollableTableFrame(self._table))

        self._render_sources()
        self._apply_read_only()

    # ###### ПОБУДОВА ТАБЛИЦІ ДЖЕРЕЛ / RENDER SOURCES TABLE ######
    def _render_sources(self) -> None:
        """Renders trusted sources table with checkboxes and active controls."""

        self._table.itemChanged.disconnect(self._on_table_item_changed)
        self._table.setRowCount(0)
        for row_index, source in enumerate(self._sources):
            self._table.insertRow(row_index)

            # Колонка 0: чекбокс вибору
            select_checkbox = QCheckBox()
            select_checkbox.setEnabled(not self._read_only)
            select_checkbox.stateChanged.connect(self._update_delete_button)
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(select_checkbox)
            cell_layout.setContentsMargins(4, 0, 4, 0)
            self._table.setCellWidget(row_index, 0, cell_widget)

            self._table.setItem(row_index, 1, QTableWidgetItem(source.source_name))
            kind_map = {NewsSourceKind.NPA.value: "НПА", NewsSourceKind.NEWS.value: "Новини"}
            self._table.setItem(row_index, 2, QTableWidgetItem(kind_map.get(source.source_kind.value, source.source_kind.value)))

            # Колонка 3: чекбокс активності
            active_checkbox = QCheckBox()
            active_checkbox.setChecked(source.is_active)
            active_checkbox.setEnabled(not self._read_only)
            active_checkbox.stateChanged.connect(
                lambda _state, source_id=source.source_id, widget=active_checkbox: self.source_toggled.emit(
                    source_id, widget.isChecked()
                )
            )
            active_cell = QWidget()
            active_layout = QHBoxLayout(active_cell)
            active_layout.addWidget(active_checkbox)
            active_layout.setContentsMargins(4, 0, 4, 0)
            self._table.setCellWidget(row_index, 3, active_cell)

            last_checked = source.last_checked_at_text or "ще не перевірялось"
            self._table.setItem(row_index, 4, QTableWidgetItem(last_checked))

        self._table.resizeColumnToContents(0)
        self._table.itemChanged.connect(self._on_table_item_changed)

    # ###### ОНОВЛЕННЯ КНОПКИ ВИДАЛЕННЯ / UPDATE DELETE BUTTON STATE ######
    def _update_delete_button(self) -> None:
        """Enables delete button when at least one source is selected."""

        selected_ids = self._get_selected_source_ids()
        self._delete_button.setEnabled(bool(selected_ids) and not self._read_only)

    # ###### ОТРИМАННЯ ОБРАНИХ ID / GET SELECTED SOURCE IDS ######
    def _get_selected_source_ids(self) -> list[int]:
        """Returns source_ids for rows with checked selection checkboxes."""

        selected: list[int] = []
        for row_index, source in enumerate(self._sources):
            cell_widget = self._table.cellWidget(row_index, 0)
            if cell_widget is None:
                continue
            checkbox = cell_widget.findChild(QCheckBox)
            if checkbox is not None and checkbox.isChecked():
                selected.append(source.source_id)
        return selected

    # ###### ВИДАЛЕННЯ ОБРАНИХ / EMIT DELETE SELECTED ######
    def _emit_delete_selected(self) -> None:
        """Emits request to delete selected sources."""

        selected_ids = self._get_selected_source_ids()
        if selected_ids:
            self.sources_deleted.emit(selected_ids)

    # ###### ДІАЛОГ НАЛАШТУВАННЯ РОЗКЛАДУ / OPEN SCHEDULE DIALOG ######
    def _open_schedule_dialog(self) -> None:
        """Opens a dialog to set the daily news refresh time."""

        from osah.ui.qt.design.tokens import COLOR, SPACING

        dialog = QDialog(self)
        dialog.setWindowTitle("Налаштувати розклад перевірки")
        dialog.setModal(True)
        dialog.setFixedWidth(360)
        dialog.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        dlg_layout.setSpacing(SPACING["md"])

        label = QLabel("Щоденний час автоматичної перевірки новин:")
        dlg_layout.addWidget(label)

        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(QTime.fromString(self._news_refresh_time, "HH:mm"))
        dlg_layout.addWidget(time_edit)

        buttons_row = QHBoxLayout()
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_row.addWidget(cancel_btn)
        buttons_row.addStretch()
        save_btn = QPushButton("Зберегти")
        save_btn.setProperty("variant", "accent")
        save_btn.clicked.connect(dialog.accept)
        buttons_row.addWidget(save_btn)
        dlg_layout.addLayout(buttons_row)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_time = time_edit.time().toString("HH:mm")
            self._news_refresh_time = selected_time
            self.refresh_time_saved.emit(selected_time)


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

    # ###### ОБРОБНИК ЗМІНИ ЕЛЕМЕНТА / TABLE ITEM CHANGED ######
    def _on_table_item_changed(self) -> None:
        """Stub handler to avoid unconnected signal warnings."""
