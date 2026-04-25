from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_medical_workspace import load_medical_workspace
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.medical_workspace import MedicalWorkspace
from osah.domain.entities.medical_workspace_mode import MedicalWorkspaceMode
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.ui.qt.components.screen_states import EmptyStateWidget, ErrorStateWidget, LoadingStateWidget
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.medical.medical_filter_bar import MedicalFilterBar
from osah.ui.qt.screens.medical.medical_record_details_pane import MedicalRecordDetailsPane
from osah.ui.qt.screens.medical.medical_registry_table import MedicalRegistryTable
from osah.ui.qt.screens.medical.medical_summary_panel import MedicalSummaryPanel
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController
from osah.ui.qt.workers.workspace_reload_worker import WorkspaceReloadWorker


class MedicalScreen(QWidget):
    """Full Qt screen for medical admission and restrictions module."""

    employee_open_requested = Signal(str)

    def __init__(self, database_path: Path, workspace: MedicalWorkspace, initial_status: str | None = None) -> None:
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
            "Медицина",
            "Контроль меддопуску, строків дії та робочих обмежень без зберігання діагнозів.",
        )
        layout.addWidget(self._section_header)

        self.summary_panel = MedicalSummaryPanel(workspace.summary)
        layout.addWidget(self.summary_panel)
        self.filter_bar = MedicalFilterBar(workspace)
        self.filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self.filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.registry_table = MedicalRegistryTable()
        self.registry_table.row_selected.connect(self._show_row)
        splitter.addWidget(ScrollableTableFrame(self.registry_table))

        self.details_pane = MedicalRecordDetailsPane(database_path, workspace.employees)
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
        """Reloads data after creating or editing medical record."""

        if not self._reload_task_controller.start_worker(
            WorkspaceReloadWorker(
                load_callable=lambda: load_medical_workspace(self._database_path),
                operation_label="Оновлення реєстру медицини",
            )
        ):
            self.error_state.show_state("Оновлення вже виконується. Дочекайтеся завершення.")

    # ###### ЗАСТОСУВАННЯ ФІЛЬТРІВ / APPLY FILTERS ######
    def _apply_filters(self) -> None:
        """Applies combined filters without domain calculations in UI."""

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches(row, values))
        if values["mode"] == MedicalWorkspaceMode.BY_EMPLOYEES.value:
            rows = _collapse_by_employee(rows)
        self.registry_table.set_rows(rows)
        self.loading_state.hide()
        self.error_state.hide()
        if rows:
            self.empty_state.hide()
        else:
            self.empty_state.show_state(
                "Немає медичних записів за активними фільтрами.",
                "Змініть параметри пошуку або перевірте актуальність записів.",
            )
        self.registry_table.select_first()

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def _show_row(self, row: MedicalWorkspaceRow) -> None:
        """Shows selected medical row in details pane."""

        self.details_pane.show_row(row)

    # ###### СТАРТОВИЙ ФІЛЬТР СТАТУСУ / INITIAL STATUS FILTER ######
    def _apply_initial_status(self, initial_status: str) -> None:
        """Activates initial status filter from navigation intent."""

        try:
            self.filter_bar.set_status_filter(MedicalStatus(initial_status))
        except ValueError:
            return

    # ###### СТАРТ ПЕРЕЗАВАНТАЖЕННЯ / RELOAD START ######
    def _on_reload_started(self) -> None:
        """Applies busy-state for workspace reload."""

        self.loading_state.show_state("Оновлення реєстру медицини...")
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

        if not isinstance(payload, MedicalWorkspace):
            self.error_state.show_state("Отримано некоректний результат оновлення реєстру медицини.")
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
def _row_matches(row: MedicalWorkspaceRow, values: dict[str, str | bool]) -> bool:
    """Checks whether row matches active filters."""

    haystack = " ".join(
        (
            row.employee_full_name,
            row.employee_personnel_number,
            row.department_name,
            row.site_name,
            row.position_name,
            row.decision_label,
            row.restriction_note,
            row.status_reason,
        )
    ).lower()
    if values["search"] and str(values["search"]) not in haystack:
        return False
    if values["department"] and row.department_name != values["department"]:
        return False
    if values["site"] and row.site_name != values["site"]:
        return False
    if values["position"] and row.position_name != values["position"]:
        return False
    if values["employee"] and row.employee_personnel_number != values["employee"]:
        return False
    if values["status"] and row.status.value != values["status"]:
        return False
    if values["restricted_only"] and not row.has_restriction:
        return False
    return True


# ###### ЗГОРТАННЯ ДО ПРАЦІВНИКА / COLLAPSE BY EMPLOYEE ######
def _collapse_by_employee(rows: tuple[MedicalWorkspaceRow, ...]) -> tuple[MedicalWorkspaceRow, ...]:
    """Keeps most problematic medical row per employee."""

    priority = {
        MedicalStatus.NOT_FIT: 5,
        MedicalStatus.EXPIRED: 4,
        MedicalStatus.RESTRICTED: 3,
        MedicalStatus.WARNING: 2,
        MedicalStatus.CURRENT: 1,
    }
    selected: dict[str, MedicalWorkspaceRow] = {}
    for row in rows:
        current = selected.get(row.employee_personnel_number)
        if current is None or priority[row.status] > priority[current.status]:
            selected[row.employee_personnel_number] = row
    return tuple(selected.values())
