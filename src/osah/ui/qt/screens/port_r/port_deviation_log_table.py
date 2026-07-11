from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QTableWidget, QTableWidgetItem

from osah.domain.entities.port_shift_checklist_row import PortShiftChecklistRow
from osah.domain.entities.port_shift_decision import format_port_shift_decision
from osah.domain.entities.port_shift_zone import PortShiftZone, format_port_shift_zone
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem
from osah.ui.qt.design.tokens import COLOR

_ZONE_BADGE_STYLES: dict[PortShiftZone, str] = {
    PortShiftZone.GREEN: (
        f"background: {COLOR['status_ok_bg']}; color: {COLOR['status_ok_text']};"
        f" border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: bold;"
    ),
    PortShiftZone.YELLOW: (
        f"background: {COLOR['status_warning_bg']}; color: {COLOR['status_warning_text']};"
        f" border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: bold;"
    ),
    PortShiftZone.RED: (
        f"background: {COLOR['status_critical_bg']}; color: {COLOR['status_critical_text']};"
        f" border-radius: 3px; padding: 2px 6px; font-size: 10px; font-weight: bold;"
    ),
}

_COL_DATE = 0
_COL_SHIFT = 1
_COL_PASSPORT = 2
_COL_TRIGGERED = 3
_COL_RDYN = 4
_COL_ZONE = 5
_COL_DECISION = 6
_COL_BARRIER = 7
_COL_RESPONSIBLE = 8

_WRAP_COLUMNS = frozenset(
    {
        _COL_PASSPORT,
        _COL_TRIGGERED,
        _COL_DECISION,
        _COL_BARRIER,
        _COL_RESPONSIBLE,
    }
)
_MIN_ROW_HEIGHT = 34


class PortDeviationLogTable(QTableWidget):
    """Таблиця журналу відхилень змін ПОРТ-Р.
    Table of PORT-R shift deviation log records.
    """

    record_activated = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 9)
        self.setHorizontalHeaderLabels(
            [
                "Дата",
                "Зміна",
                "Паспорт / ділянка",
                "Спрацьовані блоки",
                "R_dyn",
                "Зона",
                "Рішення",
                "Бар'єри",
                "Відповідальний",
            ]
        )
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
        self.horizontalHeader().setStretchLastSection(True)
        header = self.horizontalHeader()
        header.setSectionResizeMode(_COL_DECISION, QHeaderView.ResizeMode.Stretch)
        header.setStyleSheet(
            f"QHeaderView::section {{ padding-left: 8px; padding-right: {8 + 5}px; }}"
        )
        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(_COL_DATE, Qt.SortOrder.DescendingOrder)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        row_key = item.data(ROW_KEY_ROLE)
        try:
            self.record_activated.emit(int(row_key))
        except (TypeError, ValueError):
            return

    def set_rows(self, rows: tuple[PortShiftChecklistRow, ...]) -> None:
        """Перемальовує таблицю журналу відхилень.
        Redraws the deviation log table.
        """

        self.setSortingEnabled(False)
        self.setRowCount(0)

        for row_index, row in enumerate(rows):
            self.insertRow(row_index)
            r_dyn_text = f"{row.r_dyn:.3f}" if row.r_dyn is not None else "—"
            decision_text = format_port_shift_decision(row.decision) if row.decision else "—"
            passport_label = f"{row.passport_code} / {row.site_name}"

            specs = (
                (_COL_DATE, row.shift_date, row.shift_date),
                (_COL_SHIFT, row.shift_label, row.shift_label),
                (_COL_PASSPORT, passport_label, passport_label),
                (_COL_TRIGGERED, row.triggered_macrovariables or "—", row.triggered_macrovariables),
                (_COL_RDYN, r_dyn_text, row.r_dyn or 0.0),
                (_COL_ZONE, "", ""),
                (_COL_DECISION, decision_text, row.decision.value if row.decision else ""),
                (_COL_BARRIER, row.active_barrier_name or "—", row.active_barrier_name),
                (_COL_RESPONSIBLE, row.responsible_person, row.responsible_person),
            )
            row_key = str(row.checklist_id)
            for col, text, sort_val in specs:
                item = SortableTableWidgetItem(text, row_key=row_key, sort_value=sort_val)
                item.setToolTip(text)
                if col in _WRAP_COLUMNS:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                self.setItem(row_index, col, item)

            if row.zone is not None:
                zone_label = QLabel(format_port_shift_zone(row.zone))
                zone_label.setWordWrap(True)
                zone_label.setAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                zone_label.setStyleSheet(_ZONE_BADGE_STYLES[row.zone])
                zone_label.setContentsMargins(4, 2, 4, 2)
                self.setCellWidget(row_index, _COL_ZONE, zone_label)

        self.resizeColumnsToContents()
        ensure_table_column_width(self, _COL_PASSPORT, max_width=280)
        ensure_table_column_width(self, _COL_TRIGGERED, max_width=160)
        ensure_table_column_width(self, _COL_ZONE, max_width=150)
        ensure_table_column_width(self, _COL_BARRIER, max_width=220)
        zone_col_width = self.columnWidth(_COL_ZONE)
        for row_index in range(self.rowCount()):
            zone_widget = self.cellWidget(row_index, _COL_ZONE)
            if zone_widget is not None:
                zone_widget.setFixedWidth(max(zone_col_width - 4, 80))
        self.resizeRowsToContents()
        for row_index in range(self.rowCount()):
            row_height = self.rowHeight(row_index)
            if row_height < _MIN_ROW_HEIGHT:
                row_height = _MIN_ROW_HEIGHT
            zone_widget = self.cellWidget(row_index, _COL_ZONE)
            if zone_widget is not None:
                zone_height = zone_widget.sizeHint().height() + 8
                if zone_height > row_height:
                    row_height = zone_height
            self.setRowHeight(row_index, row_height)

        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicator(_COL_DATE, Qt.SortOrder.DescendingOrder)
