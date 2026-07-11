from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget

from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus, format_port_passport_risk_status
from osah.domain.entities.port_risk_level import PORT_RISK_LEVEL_LABELS, PortRiskLevel
from osah.domain.entities.port_site_risk import PortSiteRisk
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem

_STATUS_SORT_ORDER = {
    PortPassportRiskStatus.ACCEPTED: 0,
    PortPassportRiskStatus.MANUAL: 1,
    PortPassportRiskStatus.SUGGESTED: 2,
    PortPassportRiskStatus.REJECTED: 3,
}

_MIN_ROW_HEIGHT = 44


class PortSiteRisksTable(QTableWidget):
    """Таблиця ризиків конкретного паспорта ділянки ПОРТ-Р.
    Table of risks for a specific PORT-R site passport.
    """

    row_selected = Signal(object)  # PortSiteRisk

    def __init__(self) -> None:
        super().__init__(0, 4)
        self._rows_by_key: dict[str, PortSiteRisk] = {}
        self._default_sort_column = 0
        self.setHorizontalHeaderLabels(["Статус", "Ризикова ситуація", "Рівень ризику", "Джерело"])
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
            """
        )
        header = self.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(self._default_sort_column, Qt.SortOrder.AscendingOrder)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.setSortingEnabled(True)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: tuple[PortSiteRisk, ...]) -> None:
        """Перемальовує таблицю під актуальний список ризиків паспорта.
        Redraws the table for the current passport risk list.
        """

        self._rows_by_key = {self._row_key(row): row for row in rows}
        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)

            status_item = SortableTableWidgetItem(
                format_port_passport_risk_status(row.status),
                row_key=self._row_key(row),
                sort_value=_STATUS_SORT_ORDER.get(row.status, 99),
            )
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row_index, 0, status_item)

            situation_item = SortableTableWidgetItem(
                row.risk_situation,
                row_key=self._row_key(row),
                sort_value=row.risk_situation,
            )
            situation_item.setToolTip(row.risk_situation)
            self.setItem(row_index, 1, situation_item)

            level_label = _format_level(row.risk_level)
            level_item = SortableTableWidgetItem(
                level_label,
                row_key=self._row_key(row),
                sort_value=_level_priority(row.risk_level),
            )
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row_index, 2, level_item)

            source_label = "Реєстр" if row.addition_source == "registry" else "Вручну"
            source_item = SortableTableWidgetItem(
                source_label,
                row_key=self._row_key(row),
                sort_value=source_label,
            )
            source_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row_index, 3, source_item)

        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)
        self.resizeRowsToContents()
        for i in range(self.rowCount()):
            if self.rowHeight(i) < _MIN_ROW_HEIGHT:
                self.setRowHeight(i, _MIN_ROW_HEIGHT)

    def current_risk(self) -> PortSiteRisk | None:
        """Повертає вибраний ризик або None.
        Returns the selected risk or None.
        """

        selected = self.selectedItems()
        if not selected:
            return None
        row_key = str(selected[0].data(ROW_KEY_ROLE))
        return self._rows_by_key.get(row_key)

    def select_first(self) -> None:
        if self.rowCount():
            self.selectRow(0)

    def _emit_selected_row(self) -> None:
        risk = self.current_risk()
        if risk is not None:
            self.row_selected.emit(risk)

    def _row_key(self, row: PortSiteRisk) -> str:
        return str(row.risk_id)


def _format_level(risk_level: str) -> str:
    if not risk_level:
        return "—"
    try:
        return PORT_RISK_LEVEL_LABELS[PortRiskLevel(risk_level)]
    except (ValueError, KeyError):
        return risk_level


def _level_priority(risk_level: str) -> int:
    priorities = {
        PortRiskLevel.LOW.value: 1,
        PortRiskLevel.MEDIUM.value: 2,
        PortRiskLevel.HIGH.value: 3,
        PortRiskLevel.CRITICAL.value: 4,
    }
    return priorities.get(risk_level, 0)
