from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QPushButton, QTableWidget

from osah.domain.entities.port_risk_suggestion import PortRiskSuggestion
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem

_MIN_ROW_HEIGHT = 44
_SCORE_COL_WIDTH = 90
_ACTION_COL_WIDTH = 104


class PortRiskSuggestionsTable(QTableWidget):
    """Таблиця рекомендованих ризиків для вибраного паспорта ПОРТ-Р."""

    add_requested = Signal(object)  # PortRiskSuggestion

    def __init__(self) -> None:
        super().__init__(0, 3)
        self._rows_by_key: dict[str, PortRiskSuggestion] = {}
        self._default_sort_column = 1
        self.setHorizontalHeaderLabels(["Ризикова ситуація", "Бал збігу\nпо тегах", "Дія"])
        self.horizontalHeader().setFixedHeight(44)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.verticalHeader().setVisible(False)
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
            QPushButton {
                min-height: 34px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 800;
            }
            """
        )
        header = self.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(self._default_sort_column, Qt.SortOrder.DescendingOrder)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(1, _SCORE_COL_WIDTH)
        self.setColumnWidth(2, _ACTION_COL_WIDTH)
        self.setSortingEnabled(True)

    def set_rows(self, rows: tuple[PortRiskSuggestion, ...]) -> None:
        """Перемальовує таблицю під актуальний список рекомендованих ризиків.
        Redraws the table for the current suggested risk list.
        """

        self._rows_by_key = {self._row_key(row): row for row in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)

            situation_item = SortableTableWidgetItem(
                row.risk_situation,
                row_key=self._row_key(row),
                sort_value=row.risk_situation,
            )
            situation_item.setToolTip(row.risk_situation)
            self.setItem(row_index, 0, situation_item)

            score_item = SortableTableWidgetItem(
                str(row.score),
                row_key=self._row_key(row),
                sort_value=row.score,
            )
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row_index, 1, score_item)

            dummy_item = SortableTableWidgetItem("", row_key=self._row_key(row), sort_value="")
            self.setItem(row_index, 2, dummy_item)

            btn = QPushButton("Додати")
            btn.setProperty("variant", "accent")
            btn.clicked.connect(_make_add_handler(self, row))
            self.setCellWidget(row_index, 2, btn)

        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)
        self.resizeRowsToContents()
        for i in range(self.rowCount()):
            if self.rowHeight(i) < _MIN_ROW_HEIGHT:
                self.setRowHeight(i, _MIN_ROW_HEIGHT)

    def _row_key(self, row: PortRiskSuggestion) -> str:
        return str(row.registry_risk_id)


def _make_add_handler(table: PortRiskSuggestionsTable, row: PortRiskSuggestion):
    """Повертає замикання для кнопки «Додати» конкретного рядка.
    Returns a closure for the 'Add' button of a specific row.
    """

    def handler() -> None:
        table.add_requested.emit(row)

    return handler
