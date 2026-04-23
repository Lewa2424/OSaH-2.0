from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_work_permit_workspace import load_work_permit_workspace
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_workspace import WorkPermitWorkspace
from osah.domain.entities.work_permit_workspace_mode import WorkPermitWorkspaceMode
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.work_permits.work_permit_details_pane import WorkPermitDetailsPane
from osah.ui.qt.screens.work_permits.work_permit_summary_panel import WorkPermitSummaryPanel
from osah.ui.qt.screens.work_permits.work_permits_filter_bar import WorkPermitsFilterBar
from osah.ui.qt.screens.work_permits.work_permits_registry_table import WorkPermitsRegistryTable


class WorkPermitsScreen(QWidget):
    """Повноцінний Qt-екран модуля нарядів-допусків.
    Full Qt screen for the work permits module.
    """

    employee_open_requested = Signal(str)

    def __init__(self, database_path: Path, workspace: WorkPermitWorkspace, initial_status: str | None = None) -> None:
        super().__init__()
        self._database_path = database_path
        self._workspace = workspace
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Наряди-допуски")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)
        subtitle = QLabel("Оперативний контроль активних, прострочених, закритих і проблемних допусків до робіт.")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        self.summary_panel = WorkPermitSummaryPanel(workspace.summary)
        layout.addWidget(self.summary_panel)
        self.filter_bar = WorkPermitsFilterBar(workspace)
        self.filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self.filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.registry_table = WorkPermitsRegistryTable()
        self.registry_table.row_selected.connect(self._show_row)
        splitter.addWidget(self.registry_table)
        self.details_pane = WorkPermitDetailsPane(database_path, workspace.employees)
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

    # ###### ОНОВЛЕННЯ ДАНИХ / RELOAD DATA ######
    def _reload_workspace(self) -> None:
        """Перезавантажує дані після створення, редагування, закриття або скасування наряду.
        Reloads data after creating, editing, closing or canceling a work permit.
        """

        self._workspace = load_work_permit_workspace(self._database_path)
        self.summary_panel.set_summary(self._workspace.summary)
        self._apply_filters()

    # ###### ФІЛЬТРИ / FILTERS ######
    def _apply_filters(self) -> None:
        """Застосовує комбіновані фільтри без доменних розрахунків у UI.
        Applies combined filters without domain calculations in UI.
        """

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches(row, values))
        if values["mode"] == WorkPermitWorkspaceMode.BY_EMPLOYEES.value:
            rows = _collapse_by_employee(rows)
        elif values["mode"] == WorkPermitWorkspaceMode.ACTIVE_WORKS.value:
            rows = tuple(row for row in rows if row.status in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING, WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID})
        self.registry_table.set_rows(rows)
        self.empty_state.setText("" if rows else "Нічого не знайдено. Змініть фільтри або скиньте пошук.")
        self.registry_table.select_first()

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def _show_row(self, row: WorkPermitWorkspaceRow) -> None:
        """Показує вибраний наряд у правій панелі.
        Shows the selected work permit in the right pane.
        """

        self.details_pane.show_row(row)

    # ###### СТАРТОВИЙ ФІЛЬТР / INITIAL FILTER ######
    def _apply_initial_status(self, initial_status: str) -> None:
        """Активує стартовий фільтр статусу з navigation intent.
        Activates initial status filter from navigation intent.
        """

        try:
            self.filter_bar.set_status_filter(WorkPermitStatus(initial_status))
        except ValueError:
            return


# ###### ПЕРЕВІРКА ФІЛЬТРІВ / FILTER MATCH ######
def _row_matches(row: WorkPermitWorkspaceRow, values: dict[str, str | bool]) -> bool:
    """Перевіряє відповідність рядка активним фільтрам.
    Checks whether a row matches active filters.
    """

    haystack = " ".join((row.permit_number, row.work_kind, row.work_location, row.responsible_person, row.issuer_person, row.participant_names)).lower()
    if values["search"] and str(values["search"]) not in haystack:
        return False
    if values["status"] and row.status.value != values["status"]:
        return False
    if values["work_kind"] and row.work_kind != values["work_kind"]:
        return False
    if values["department"] and row.department_name != values["department"]:
        return False
    if values["employee"] and values["employee"] not in row.employee_numbers:
        return False
    if values["problem_only"] and not (row.has_conflicts or row.status in {WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID}):
        return False
    if values["active_only"] and row.status not in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING, WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID}:
        return False
    return True


# ###### ЗГОРТАННЯ ДО ПРАЦІВНИКА / COLLAPSE BY EMPLOYEE ######
def _collapse_by_employee(rows: tuple[WorkPermitWorkspaceRow, ...]) -> tuple[WorkPermitWorkspaceRow, ...]:
    """Залишає для кожного учасника найпроблемніший наряд.
    Keeps the most problematic work permit for each participant.
    """

    priority = {
        WorkPermitStatus.INVALID: 5,
        WorkPermitStatus.EXPIRED: 4,
        WorkPermitStatus.WARNING: 3,
        WorkPermitStatus.ACTIVE: 2,
        WorkPermitStatus.CLOSED: 1,
        WorkPermitStatus.CANCELED: 0,
    }
    selected: dict[str, WorkPermitWorkspaceRow] = {}
    for row in rows:
        for employee_number in row.employee_numbers:
            current = selected.get(employee_number)
            if current is None or priority[row.status] > priority[current.status] or row.has_conflicts:
                selected[employee_number] = row
    return tuple(selected.values())
