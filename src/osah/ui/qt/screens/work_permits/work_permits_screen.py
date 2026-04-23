from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_work_permit_workspace import load_work_permit_workspace
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_workspace import WorkPermitWorkspace
from osah.domain.entities.work_permit_workspace_mode import WorkPermitWorkspaceMode
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.ui.qt.components.screen_states import EmptyStateWidget, ErrorStateWidget, LoadingStateWidget
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.work_permits.work_permit_details_pane import WorkPermitDetailsPane
from osah.ui.qt.screens.work_permits.work_permit_summary_panel import WorkPermitSummaryPanel
from osah.ui.qt.screens.work_permits.work_permits_filter_bar import WorkPermitsFilterBar
from osah.ui.qt.screens.work_permits.work_permits_registry_table import WorkPermitsRegistryTable
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController
from osah.ui.qt.workers.workspace_reload_worker import WorkspaceReloadWorker


class WorkPermitsScreen(QWidget):
    """Full Qt screen for work permits module."""

    employee_open_requested = Signal(str)

    def __init__(self, database_path: Path, workspace: WorkPermitWorkspace, initial_status: str | None = None) -> None:
        super().__init__()
        self._database_path = database_path
        self._workspace = workspace

        self._reload_task_controller = WorkerTaskController()
        self._reload_task_controller.started.connect(self._on_reload_started)
        self._reload_task_controller.progress.connect(self._on_reload_progress)
        self._reload_task_controller.success.connect(self._on_reload_success)
        self._reload_task_controller.error.connect(self._on_reload_error)
        self._reload_task_controller.finished.connect(self._on_reload_finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        self._section_header = SectionHeader(
            "Наряди-допуски",
            "Оперативний контроль активних, прострочених, закритих і проблемних допусків до робіт.",
        )
        layout.addWidget(self._section_header)

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

        self.loading_state = LoadingStateWidget()
        self.error_state = ErrorStateWidget()
        self.empty_state = EmptyStateWidget()
        layout.addWidget(self.loading_state)
        layout.addWidget(self.error_state)
        layout.addWidget(self.empty_state)

        if initial_status:
            self._apply_initial_status(initial_status)
        self._apply_filters()

    # ###### ОНОВЛЕННЯ ДАНИХ / RELOAD DATA ######
    def _reload_workspace(self) -> None:
        """Reloads data after creating, editing, closing or canceling permit."""

        if not self._reload_task_controller.start_worker(
            WorkspaceReloadWorker(
                load_callable=lambda: load_work_permit_workspace(self._database_path),
                operation_label="Оновлення реєстру нарядів-допусків",
            )
        ):
            self.error_state.show_state("Оновлення вже виконується. Дочекайтеся завершення.")

    # ###### ФІЛЬТРИ / APPLY FILTERS ######
    def _apply_filters(self) -> None:
        """Applies combined filters without domain calculations in UI."""

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches(row, values))
        if values["mode"] == WorkPermitWorkspaceMode.BY_EMPLOYEES.value:
            rows = _collapse_by_employee(rows)
        elif values["mode"] == WorkPermitWorkspaceMode.ACTIVE_WORKS.value:
            rows = tuple(
                row
                for row in rows
                if row.status
                in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING, WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID}
            )
        self.registry_table.set_rows(rows)
        self.loading_state.hide()
        self.error_state.hide()
        if rows:
            self.empty_state.hide()
        else:
            self.empty_state.show_state(
                "Немає нарядів-допусків за поточними фільтрами.",
                "Скиньте фільтри або перевірте активні роботи.",
            )
        self.registry_table.select_first()

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def _show_row(self, row: WorkPermitWorkspaceRow) -> None:
        """Shows selected permit in details pane."""

        self.details_pane.show_row(row)

    # ###### СТАРТОВИЙ ФІЛЬТР СТАТУСУ / INITIAL STATUS FILTER ######
    def _apply_initial_status(self, initial_status: str) -> None:
        """Activates initial status filter from navigation intent."""

        try:
            self.filter_bar.set_status_filter(WorkPermitStatus(initial_status))
        except ValueError:
            return

    # ###### СТАРТ ПЕРЕЗАВАНТАЖЕННЯ / RELOAD START ######
    def _on_reload_started(self) -> None:
        """Applies busy-state for workspace reload."""

        self.loading_state.show_state("Оновлення реєстру нарядів-допусків...")
        self.error_state.hide()
        self.filter_bar.setEnabled(False)
        self.details_pane.setEnabled(False)

    # ###### ПРОГРЕС ПЕРЕЗАВАНТАЖЕННЯ / RELOAD PROGRESS ######
    def _on_reload_progress(self, progress_value: int, message_text: str) -> None:
        """Updates loading message while reload is running."""

        self.loading_state.show_state(message_text)

    # ###### УСПІХ ПЕРЕЗАВАНТАЖЕННЯ / RELOAD SUCCESS ######
    def _on_reload_success(self, payload: object) -> None:
        """Updates workspace from background reload result."""

        if not isinstance(payload, WorkPermitWorkspace):
            self.error_state.show_state("Отримано некоректний результат оновлення реєстру нарядів-допусків.")
            return
        self._workspace = payload
        self.summary_panel.set_summary(self._workspace.summary)
        self._apply_filters()

    # ###### ПОМИЛКА ПЕРЕЗАВАНТАЖЕННЯ / RELOAD ERROR ######
    def _on_reload_error(self, message_text: str) -> None:
        """Shows reload error text."""

        self.error_state.show_state(message_text)

    # ###### ФІНАЛ ПЕРЕЗАВАНТАЖЕННЯ / RELOAD FINISH ######
    def _on_reload_finished(self) -> None:
        """Resets busy-state after reload completion."""

        self.loading_state.hide()
        self.filter_bar.setEnabled(True)
        self.details_pane.setEnabled(True)


# ###### ПЕРЕВІРКА ФІЛЬТРІВ / FILTER MATCH ######
def _row_matches(row: WorkPermitWorkspaceRow, values: dict[str, str | bool]) -> bool:
    """Checks whether row matches active filters."""

    haystack = " ".join(
        (row.permit_number, row.work_kind, row.work_location, row.responsible_person, row.issuer_person, row.participant_names)
    ).lower()
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
    if values["active_only"] and row.status not in {
        WorkPermitStatus.ACTIVE,
        WorkPermitStatus.WARNING,
        WorkPermitStatus.EXPIRED,
        WorkPermitStatus.INVALID,
    }:
        return False
    return True


# ###### ЗГОРТАННЯ ДО ПРАЦІВНИКА / COLLAPSE BY EMPLOYEE ######
def _collapse_by_employee(rows: tuple[WorkPermitWorkspaceRow, ...]) -> tuple[WorkPermitWorkspaceRow, ...]:
    """Keeps most problematic permit per participant."""

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
