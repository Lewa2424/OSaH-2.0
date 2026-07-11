from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QPushButton, QTableWidget, QWidget

from osah.domain.entities.port_passport_status import format_port_passport_status
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import format_port_risk_profile
from osah.domain.entities.port_site_passport_row import PortSitePassportRow
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem


class PortSitePassportsTable(QTableWidget):
    """Таблиця паспортів ділянок ПОРТ-Р.
    Table of PORT-R site passports.
    """

    row_selected = Signal(object)
    edit_requested = Signal(object)
    archive_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__(0, 7)
        self._rows_by_key: dict[str, PortSitePassportRow] = {}
        self._default_sort_column = 5
        self.setHorizontalHeaderLabels(
            [
                "Код / № паспорта",
                "Назва ділянки",
                "Тип ділянки",
                "Профіль ризику",
                "Статус",
                "Дата оновлення",
                "Дії",
            ]
        )
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.setStyleSheet(
            """
            QTableWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #D6E1EC;
                border-radius: 18px;
                gridline-color: #E2EAF2;
                font-size: 14px;
            }
            QHeaderView::section {
                background: #EAF1F7;
                color: #17365D;
                padding: 11px 8px;
                border: none;
                font-size: 13px;
                font-weight: 800;
            }
            """
        )
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(self._default_sort_column, Qt.SortOrder.DescendingOrder)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[PortSitePassportRow, ...]) -> None:
        """Перемальовує таблицю під актуальний список паспортів.
        Redraws the table for the current passport list.
        """

        self._rows_by_key = {self._row_key(row): row for row in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            cell_specs = (
                (0, row.passport_code, row.passport_code),
                (1, row.site_name, row.site_name),
                (2, row.site_type or "-", row.site_type),
                (3, format_port_risk_profile(row.final_profile), row.final_profile.value),
                (4, format_port_passport_status(row.status), row.status.value),
                (5, format_ui_datetime(row.updated_at), row.updated_at),
                (6, "", ""),
            )
            for column_index, text, sort_value in cell_specs:
                self._set_item(row_index, column_index, text, row, sort_value=sort_value)
            self.setCellWidget(row_index, 6, self._build_actions_cell(row))
            self.setRowHeight(row_index, 38)

        self.resizeColumnsToContents()
        ensure_table_column_width(self, 1, max_width=360)
        ensure_table_column_width(self, 6, max_width=78)
        self.setColumnWidth(1, max(self.columnWidth(1), 180))
        self.setColumnWidth(6, 72)
        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)

    def select_first(self) -> None:
        """Вибирає перший паспорт, якщо список не порожній.
        Selects the first passport when the list is not empty.
        """

        if self.rowCount():
            self.selectRow(0)

    def _set_item(
        self,
        row_index: int,
        column_index: int,
        text: str,
        row: PortSitePassportRow,
        *,
        sort_value: object,
    ) -> None:
        item = SortableTableWidgetItem(text, row_key=self._row_key(row), sort_value=sort_value)
        item.setToolTip(text)
        self.setItem(row_index, column_index, item)

    def _emit_selected_row(self) -> None:
        selected = self.selectedItems()
        if not selected:
            return
        row_key = str(selected[0].data(ROW_KEY_ROLE))
        row = self._rows_by_key.get(row_key)
        if row is not None:
            self.row_selected.emit(row)

    def _row_key(self, row: PortSitePassportRow) -> str:
        return str(row.passport_id)

    def _build_actions_cell(self, row: PortSitePassportRow) -> QWidget:
        cell_widget = QWidget(self)
        layout = QHBoxLayout(cell_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        emoji_font = QFont("Segoe UI Emoji", 11)

        edit_btn = QPushButton("🖉", cell_widget)
        edit_btn.setFont(emoji_font)
        edit_btn.setToolTip("Редагувати паспорт")
        edit_btn.setProperty("variant", "secondary")
        edit_btn.setFixedSize(28, 24)
        edit_btn.setStyleSheet("padding: 0px; color: #1f2a37;")
        edit_btn.setEnabled(row.status != PortPassportStatus.ARCHIVED)
        edit_btn.clicked.connect(lambda _=False, r=row: self.edit_requested.emit(r))
        layout.addWidget(edit_btn)

        archive_btn = QPushButton("🗄", cell_widget)
        archive_btn.setFont(emoji_font)
        archive_btn.setToolTip("Відправити в архів")
        archive_btn.setProperty("variant", "secondary")
        archive_btn.setFixedSize(28, 24)
        archive_btn.setStyleSheet("padding: 0px; color: #1f2a37;")
        archive_btn.setEnabled(row.status != PortPassportStatus.ARCHIVED)
        archive_btn.clicked.connect(lambda _=False, r=row: self.archive_requested.emit(r))
        layout.addWidget(archive_btn)
        return cell_widget
