from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.load_port_shift_analytics_summary import load_port_shift_analytics_summary
from osah.application.services.load_port_shift_trigger_stats import load_port_shift_trigger_stats
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_macrovariable import format_macrovariable
from osah.domain.entities.port_shift_analytics_summary import PortShiftAnalyticsSummary
from osah.domain.entities.port_shift_trigger_stat import PortShiftTriggerStat
from osah.ui.qt.components.ensure_table_column_width import ensure_table_column_width
from osah.ui.qt.components.metric_card import MetricCard
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.sortable_table_widget_item import SortableTableWidgetItem
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING

_PERIOD_OPTIONS: tuple[tuple[str, int], ...] = (
    ("7 днів", 7),
    ("14 днів", 14),
    ("30 днів", 30),
    ("90 днів", 90),
)

_COL_SITE = 0
_COL_BLOCK = 1
_COL_TRIGGER = 2
_COL_COUNT = 3
_COL_LAST = 4

_FIELD_SCALE = 0.8
_SECTION_AIR_PX = 2
_TABLE_ROW_HEIGHT = round(34 * _FIELD_SCALE)
_COMBO_MIN_WIDTH = round(140 * _FIELD_SCALE)


def _compact_combo_stylesheet() -> str:
    """Стилі фільтрів аналітики (−20% від базових полів). Analytics filter styles (−20% from base fields)."""

    radius = max(4, round(RADIUS["md"] * _FIELD_SCALE))
    return (
        f"QComboBox {{"
        f" padding: 6px 27px 6px 8px;"
        f" min-height: 19px;"
        f" font-size: 11px;"
        f" border-radius: {radius}px;"
        f"}}"
        f"QComboBox::drop-down {{"
        f" width: 24px;"
        f" border-top-right-radius: {radius}px;"
        f" border-bottom-right-radius: {radius}px;"
        f"}}"
        f"QComboBox::down-arrow {{"
        f" width: 13px;"
        f" height: 13px;"
        f"}}"
    )


def _apply_compact_field(combo: QComboBox) -> None:
    combo.setStyleSheet(_compact_combo_stylesheet())
    combo.setFixedHeight(round(32 * _FIELD_SCALE))
    combo.setMinimumWidth(_COMBO_MIN_WIDTH)


class PortRAnalyticsPanel(QWidget):
    """Вкладка «Аналітика» ПОРТ-Р: агрегація журналу змін за період і міст до калібрування порогів.
    PORT-R "Analytics" tab: shift-log aggregation over a period and a bridge to threshold calibration.
    """

    edit_thresholds_requested = Signal(int)

    def __init__(
        self,
        database_path: Path,
        access_role: AccessRole,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._database_path = database_path
        self._access_role = access_role
        self._current_passport_id: int | None = None
        self._trigger_stats: tuple[PortShiftTriggerStat, ...] = ()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACING["sm"], 0, 0)
        layout.setSpacing(_SECTION_AIR_PX)

        layout.addWidget(self._build_filters())

        self._metrics_container = QWidget()
        self._metrics_layout = QHBoxLayout(self._metrics_container)
        self._metrics_layout.setContentsMargins(0, _SECTION_AIR_PX, 0, _SECTION_AIR_PX)
        self._metrics_layout.setSpacing(_SECTION_AIR_PX)
        layout.addWidget(self._metrics_container)

        self._triggers_table = self._build_triggers_table()
        self._triggers_table.itemSelectionChanged.connect(self._update_edit_button_state)
        layout.addWidget(ScrollableTableFrame(self._triggers_table, snap_to_columns=True), stretch=1)

        self._edit_thresholds_btn = QPushButton("Відкрити пороги паспорта")
        self._edit_thresholds_btn.setProperty("variant", "accent")
        self._edit_thresholds_btn.setEnabled(False)
        self._edit_thresholds_btn.clicked.connect(self._on_edit_thresholds)
        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, _SECTION_AIR_PX, 0, 0)
        button_layout.setSpacing(_SECTION_AIR_PX)
        button_layout.addWidget(self._edit_thresholds_btn)
        button_layout.addStretch()
        layout.addWidget(button_row)

        self.reload()

    # ──────────────────────────────────────────────────────────────────────
    # Побудова UI / UI builders
    # ──────────────────────────────────────────────────────────────────────

    def _build_filters(self) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, _SECTION_AIR_PX)
        row.setSpacing(_SECTION_AIR_PX)

        row.addWidget(QLabel("Період:"))
        self._period_combo = QComboBox()
        for label, days in _PERIOD_OPTIONS:
            self._period_combo.addItem(label, days)
        self._period_combo.setCurrentIndex(2)  # 30 днів
        self._period_combo.currentIndexChanged.connect(lambda *_: self.reload())
        _apply_compact_field(self._period_combo)
        row.addWidget(self._period_combo)

        row.addWidget(QLabel("Охоплення:"))
        self._scope_combo = QComboBox()
        self._scope_combo.addItem("Усі ділянки", False)
        self._scope_combo.addItem("Поточна ділянка", True)
        self._scope_combo.currentIndexChanged.connect(lambda *_: self.reload())
        _apply_compact_field(self._scope_combo)
        row.addWidget(self._scope_combo)

        row.addStretch()
        return container

    def _build_triggers_table(self) -> QTableWidget:
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(
            ["Ділянка", "Блок", "Тригер", "Разів", "Останній раз"]
        )
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setStyleSheet(
            f"QHeaderView::section {{ padding: {_SECTION_AIR_PX + 6}px {_SECTION_AIR_PX + 8}px; }}"
        )
        table.setStyleSheet(
            f"QTableWidget {{ gridline-color: {COLOR['border_soft']}; }}"
            f"QTableWidget::item {{ padding-top: {_SECTION_AIR_PX}px; padding-bottom: {_SECTION_AIR_PX}px; }}"
        )
        table.setSortingEnabled(True)
        table.horizontalHeader().setSortIndicatorShown(True)
        return table

    # ──────────────────────────────────────────────────────────────────────
    # Публічний API / Public API
    # ──────────────────────────────────────────────────────────────────────

    def set_current_passport(self, passport_id: int | None) -> None:
        """Запам'ятовує обрану ділянку для фільтра «Поточна ділянка» та оновлює дані.
        Stores the selected site for the "current site" filter and refreshes the data.
        """

        self._current_passport_id = passport_id
        has_current = passport_id is not None
        self._scope_combo.model().item(1).setEnabled(has_current)
        if not has_current and self._scope_combo.currentData():
            self._scope_combo.setCurrentIndex(0)
        self.reload()

    def reload(self) -> None:
        """Перечитує зведення та повторювані тригери за поточними фільтрами.
        Re-reads the summary and recurring triggers for the current filters.
        """

        period_days = int(self._period_combo.currentData() or 30)
        use_current = bool(self._scope_combo.currentData()) and self._current_passport_id is not None
        passport_id = self._current_passport_id if use_current else None

        try:
            summary = load_port_shift_analytics_summary(
                self._database_path, period_days, passport_id=passport_id
            )
            self._trigger_stats = load_port_shift_trigger_stats(
                self._database_path, period_days, passport_id=passport_id
            )
        except Exception:  # noqa: BLE001
            summary = PortShiftAnalyticsSummary(0, 0, 0, 0, 0, None)
            self._trigger_stats = ()

        self._render_metrics(summary, period_days)
        self._render_triggers(self._trigger_stats)
        self._update_edit_button_state()

    # ──────────────────────────────────────────────────────────────────────
    # Рендеринг / Rendering
    # ──────────────────────────────────────────────────────────────────────

    def _render_metrics(self, summary: PortShiftAnalyticsSummary, period_days: int) -> None:
        while self._metrics_layout.count():
            item = self._metrics_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        period_label = f"за {period_days} днів"
        avg_text = f"{summary.avg_r_dyn:.2f}" if summary.avg_r_dyn is not None else "—"

        cards = (
            MetricCard("Оцінок змін", str(summary.assessments_count), period_label, COLOR["accent"], size_scale=_FIELD_SCALE),
            MetricCard("Жовта зона", str(summary.yellow_count), "обмеження / бар'єр", COLOR["status_warning_text"], size_scale=_FIELD_SCALE),
            MetricCard("Червона / STOP", f"{summary.red_count} / {summary.stop_count}", "червоних / СТОП", COLOR["status_critical_text"], size_scale=_FIELD_SCALE),
            MetricCard("Середній R_dyn", avg_text, period_label, COLOR["accent"], size_scale=_FIELD_SCALE),
        )
        for card in cards:
            self._metrics_layout.addWidget(card)

    def _render_triggers(self, stats: tuple[PortShiftTriggerStat, ...]) -> None:
        self._triggers_table.setSortingEnabled(False)
        self._triggers_table.setRowCount(0)

        for row_index, stat in enumerate(stats):
            self._triggers_table.insertRow(row_index)
            block_text = format_macrovariable(stat.macrovariable)
            trigger_text = stat.trigger_text or "—"
            if stat.is_stop_trigger:
                trigger_text = f"⛔ {trigger_text}"
            specs = (
                (_COL_SITE, f"{stat.passport_code} / {stat.site_name}", f"{stat.passport_code} / {stat.site_name}"),
                (_COL_BLOCK, block_text, stat.macrovariable.value),
                (_COL_TRIGGER, trigger_text, trigger_text),
                (_COL_COUNT, str(stat.hit_count), stat.hit_count),
                (_COL_LAST, stat.last_shift_date or "—", stat.last_shift_date),
            )
            row_key = str(stat.threshold_id)
            for col, text, sort_val in specs:
                item = SortableTableWidgetItem(text, row_key=row_key, sort_value=sort_val)
                item.setToolTip(text)
                self._triggers_table.setItem(row_index, col, item)
            self._triggers_table.setRowHeight(row_index, _TABLE_ROW_HEIGHT)

        self._triggers_table.resizeColumnsToContents()
        ensure_table_column_width(self._triggers_table, _COL_SITE, max_width=round(240 * _FIELD_SCALE))
        ensure_table_column_width(self._triggers_table, _COL_TRIGGER, max_width=round(320 * _FIELD_SCALE))
        self._triggers_table.setSortingEnabled(True)
        self._triggers_table.horizontalHeader().setSortIndicator(_COL_COUNT, Qt.SortOrder.DescendingOrder)

    # ──────────────────────────────────────────────────────────────────────
    # Дії / Actions
    # ──────────────────────────────────────────────────────────────────────

    def _selected_passport_id(self) -> int | None:
        items = self._triggers_table.selectedItems()
        if items:
            row = items[0].row()
            site_item = self._triggers_table.item(row, _COL_SITE)
            if site_item is not None:
                stat = self._stat_for_threshold(site_item.data(Qt.ItemDataRole.UserRole))
                if stat is not None:
                    return stat.passport_id
        if self._scope_combo.currentData():
            return self._current_passport_id
        return None

    def _stat_for_threshold(self, row_key: object) -> PortShiftTriggerStat | None:
        try:
            threshold_id = int(row_key)
        except (TypeError, ValueError):
            return None
        for stat in self._trigger_stats:
            if stat.threshold_id == threshold_id:
                return stat
        return None

    def _update_edit_button_state(self) -> None:
        can_edit = self._access_role == AccessRole.INSPECTOR
        self._edit_thresholds_btn.setEnabled(can_edit and self._selected_passport_id() is not None)

    def _on_edit_thresholds(self) -> None:
        passport_id = self._selected_passport_id()
        if passport_id is not None:
            self.edit_thresholds_requested.emit(passport_id)
