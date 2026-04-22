from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_ppe_workspace import load_ppe_workspace
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.ppe_workspace import PpeWorkspace
from osah.domain.entities.ppe_workspace_mode import PpeWorkspaceMode
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.ppe.ppe_filter_bar import PpeFilterBar
from osah.ui.qt.screens.ppe.ppe_problem_breakdown import PpeProblemBreakdown
from osah.ui.qt.screens.ppe.ppe_record_details_pane import PpeRecordDetailsPane
from osah.ui.qt.screens.ppe.ppe_registry_table import PpeRegistryTable
from osah.ui.qt.screens.ppe.ppe_summary_panel import PpeSummaryPanel


class PpeScreen(QWidget):
    """Повноцінний Qt-екран модуля ЗІЗ.
    Full Qt screen for the PPE module.
    """

    employee_open_requested = Signal(str)

    def __init__(self, database_path: Path, workspace: PpeWorkspace, initial_status: str | None = None) -> None:
        super().__init__()
        self._database_path = database_path
        self._workspace = workspace
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])
        title = QLabel("ЗІЗ")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)
        subtitle = QLabel("Контроль норми, факту, кількості, строків заміни та критичних відхилень.")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        self.summary_panel = PpeSummaryPanel(workspace.summary)
        layout.addWidget(self.summary_panel)
        self.filter_bar = PpeFilterBar(workspace)
        self.filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self.filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.problem_breakdown = PpeProblemBreakdown()
        center_layout.addWidget(self.problem_breakdown)
        self.registry_table = PpeRegistryTable()
        self.registry_table.row_selected.connect(self._show_row)
        center_layout.addWidget(self.registry_table, stretch=1)
        splitter.addWidget(center)

        names = tuple(sorted({row.ppe_name for row in workspace.rows}))
        self.details_pane = PpeRecordDetailsPane(database_path, workspace.employees, names)
        self.details_pane.editor.saved.connect(self._reload_workspace)
        self.details_pane.employee_requested.connect(self.employee_open_requested.emit)
        splitter.addWidget(self.details_pane)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        layout.addWidget(splitter, stretch=1)
        self.empty_state = QLabel("")
        self.empty_state.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(self.empty_state)

        if initial_status:
            self._apply_initial_status(initial_status)
        self._apply_filters()

    def _reload_workspace(self) -> None:
        """Перезавантажує дані після створення або редагування запису.
        Reloads data after creating or editing a record.
        """

        self._workspace = load_ppe_workspace(self._database_path)
        self.summary_panel.set_summary(self._workspace.summary)
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Застосовує комбіновані фільтри без доменних розрахунків у UI.
        Applies combined filters without domain calculations in UI.
        """

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches(row, values))
        if values["mode"] == PpeWorkspaceMode.BY_EMPLOYEES.value:
            rows = _collapse_by_employee(rows)
        self.registry_table.set_rows(rows)
        self.empty_state.setText("" if rows else "Нічого не знайдено. Змініть фільтри або скиньте пошук.")
        self.registry_table.select_first()

    def _show_row(self, row: PpeWorkspaceRow) -> None:
        """Показує вибрану позицію у правій панелі і breakdown.
        Shows selected item in the right pane and breakdown.
        """

        self.problem_breakdown.set_row(row)
        self.details_pane.show_row(row)

    def _apply_initial_status(self, initial_status: str) -> None:
        """Активує стартовий фільтр статусу з navigation intent.
        Activates initial status filter from navigation intent.
        """

        try:
            self.filter_bar.set_status_filter(PpeStatus(initial_status))
        except ValueError:
            return


def _row_matches(row: PpeWorkspaceRow, values: dict[str, str]) -> bool:
    """Перевіряє відповідність рядка активним фільтрам.
    Checks whether a row matches active filters.
    """

    haystack = " ".join((row.employee_full_name, row.employee_personnel_number, row.ppe_name, row.department_name, row.position_name)).lower()
    if values["search"] and values["search"] not in haystack:
        return False
    if values["ppe"] and row.ppe_name != values["ppe"]:
        return False
    if values["department"] and row.department_name != values["department"]:
        return False
    if values["status"] and row.status.value != values["status"]:
        return False
    if values["site"] and row.site_name != values["site"]:
        return False
    if values["position"] and row.position_name != values["position"]:
        return False
    if values["employee"] and row.employee_personnel_number != values["employee"]:
        return False
    return True


def _collapse_by_employee(rows: tuple[PpeWorkspaceRow, ...]) -> tuple[PpeWorkspaceRow, ...]:
    """Залишає для кожного працівника найпроблемнішу позицію ЗІЗ.
    Keeps the most problematic PPE row for each employee.
    """

    priority = {PpeStatus.NOT_ISSUED: 4, PpeStatus.EXPIRED: 3, PpeStatus.WARNING: 2, PpeStatus.CURRENT: 1}
    selected: dict[str, PpeWorkspaceRow] = {}
    for row in rows:
        current = selected.get(row.employee_personnel_number)
        if current is None or priority[row.status] > priority[current.status]:
            selected[row.employee_personnel_number] = row
    return tuple(selected.values())
