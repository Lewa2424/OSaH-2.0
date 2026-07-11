from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_training_workspace import load_training_workspace
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_workspace import TrainingWorkspace
from osah.domain.entities.training_workspace_mode import TrainingWorkspaceMode
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.ui.qt.components.configure_detail_splitter import configure_detail_splitter
from osah.ui.qt.components.install_ambient_background import install_ambient_background
from osah.ui.qt.components.screen_states import EmptyStateWidget, ErrorStateWidget, LoadingStateWidget
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.trainings.training_quick_stats import TrainingQuickStats
from osah.ui.qt.screens.trainings.training_record_details_pane import TrainingRecordDetailsPane
from osah.ui.qt.screens.trainings.trainings_filter_bar import TrainingsFilterBar
from osah.ui.qt.screens.trainings.trainings_registry_table import TrainingsRegistryTable
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController
from osah.ui.qt.workers.workspace_reload_worker import WorkspaceReloadWorker


class TrainingsScreen(QWidget):
    """Full Qt screen for the trainings module."""

    employee_open_requested = Signal(str)

    def __init__(
        self,
        database_path: Path,
        workspace: TrainingWorkspace,
        access_role: AccessRole,
        initial_status: str | None = None,
        initial_personnel_number: str | None = None,
        initial_record_id: int | None = None,
    ) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._workspace = workspace
        self._visible_rows: tuple[TrainingWorkspaceRow, ...] = workspace.rows
        self._current_row: TrainingWorkspaceRow | None = None
        self._pending_record_id: int | None = initial_record_id
        self._pending_personnel_number: str | None = initial_personnel_number

        self._reload_task_controller = WorkerTaskController()
        self._reload_task_controller.started.connect(self._on_reload_started)
        self._reload_task_controller.progress.connect(self._on_reload_progress)
        self._reload_task_controller.success.connect(self._on_reload_success)
        self._reload_task_controller.error.connect(self._on_reload_error)
        self._reload_task_controller.finished.connect(self._on_reload_finished)

        install_ambient_background(
            self,
            "trainingsScreen",
            theme="trainings",
            extra_rules="""
            QWidget#trainingsScreen QSplitter::handle { background: transparent; }
            QWidget#trainingsScreen QSplitter::handle:horizontal { width: 10px; }
            """,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        self.quick_stats = TrainingQuickStats(workspace.summary)
        layout.addWidget(self.quick_stats)

        self.filter_bar = TrainingsFilterBar(workspace)
        self.filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self.filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.registry_table = TrainingsRegistryTable()
        self.registry_table.row_selected.connect(self._show_row)
        center_layout.addWidget(ScrollableTableFrame(self.registry_table, snap_to_columns=True), stretch=1)
        splitter.addWidget(center)

        self.details_pane = TrainingRecordDetailsPane(database_path, workspace.employees, access_role)
        self.details_pane.editor.saved.connect(self._reload_workspace)
        self.details_pane.editor.deleted.connect(self._reload_workspace)
        self.details_pane.employee_requested.connect(self.employee_open_requested.emit)
        splitter.addWidget(self.details_pane)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        configure_detail_splitter(splitter, self.details_pane, detail_fraction=0.42, detail_min_width=460, detail_max_width=760)
        layout.addWidget(splitter, stretch=1)

        self.loading_state = LoadingStateWidget()
        self.error_state = ErrorStateWidget()
        self.empty_state = EmptyStateWidget()
        layout.addWidget(self.loading_state)
        layout.addWidget(self.error_state)
        layout.addWidget(self.empty_state)

        if initial_status:
            self._apply_initial_status(initial_status)
        if initial_personnel_number:
            self.filter_bar.set_employee_filter(initial_personnel_number)
        self._apply_filters()

    def _reload_workspace(self) -> None:
        """Reloads data after creating or editing a training record."""

        self._remember_selection_context()
        if not self._reload_task_controller.start_worker(
            WorkspaceReloadWorker(
                load_callable=lambda: load_training_workspace(self._database_path),
                operation_label="Оновлення реєстру інструктажів",
            )
        ):
            self.error_state.show_state("Оновлення вже виконується. Дочекайтеся завершення.")

    def _apply_filters(self) -> None:
        """Applies combined filters without domain calculations in UI."""

        if self._pending_record_id is None and self._pending_personnel_number is None:
            self._remember_selection_context()
        values = self.filter_bar.values()
        validation_error = values.get("validation_error", "").strip()
        if validation_error:
            self.registry_table.set_rows(())
            self._visible_rows = ()
            self.loading_state.hide()
            self.empty_state.hide()
            self.error_state.show_state(validation_error)
            self._current_row = None
            self.details_pane.show_empty_state()
            return
        rows = tuple(row for row in self._workspace.rows if _row_matches(row, values))
        if values["mode"] == TrainingWorkspaceMode.BY_EMPLOYEES.value:
            rows = _collapse_by_employee(rows)
        self._visible_rows = rows
        self.registry_table.set_rows(rows)
        self.loading_state.hide()
        self.error_state.hide()
        if rows:
            self.empty_state.hide()
        else:
            self.empty_state.show_state(
                "Немає записів за активними фільтрами.",
                "Скиньте фільтри або змініть параметри пошуку.",
            )
            self._current_row = None
            self.details_pane.show_empty_state()
        if rows and not self._restore_selection_context():
            self.registry_table.select_first()

    def _show_row(self, row: TrainingWorkspaceRow) -> None:
        """Shows selected row in summary and details pane."""

        self._current_row = row
        self.details_pane.show_row(row)

    def _apply_initial_status(self, initial_status: str) -> None:
        """Activates initial status filter from navigation intent."""

        try:
            self.filter_bar.set_status_filter(TrainingRegistryFilter(initial_status))
        except ValueError:
            return

    def _on_reload_started(self) -> None:
        """Applies busy-state for workspace reload."""

        self.loading_state.show_state("Оновлення реєстру інструктажів...")
        self.error_state.hide()
        self.filter_bar.setEnabled(False)
        self.details_pane.setEnabled(False)

    def _on_reload_progress(self, progress_value: int, message_text: str) -> None:
        """Updates loading message while reload is running."""

        self.loading_state.show_state(message_text)

    def _on_reload_success(self, payload: object) -> None:
        """Updates workspace from background reload result."""

        if not isinstance(payload, TrainingWorkspace):
            self.error_state.show_state("Отримано некоректний результат оновлення реєстру інструктажів.")
            return
        self._workspace = payload
        self.quick_stats.set_summary(self._workspace.summary)
        self._apply_filters()

    def _on_reload_error(self, message_text: str) -> None:
        """Shows reload error text."""

        self.error_state.show_state(message_text)

    def _on_reload_finished(self) -> None:
        """Resets busy-state after reload completion."""

        self.loading_state.hide()
        self.filter_bar.setEnabled(True)
        self.details_pane.setEnabled(True)

    def _remember_selection_context(self) -> None:
        """Запам'ятовує поточний контекст для відновлення вибору.
        Stores current context so selection can be restored later.
        """

        record_id, personnel_number = self.details_pane.editor.current_selection_context()
        if record_id is not None or personnel_number is not None:
            self._pending_record_id = record_id
            self._pending_personnel_number = personnel_number
            return
        if self._current_row is not None:
            self._pending_record_id = self._current_row.record_id
            self._pending_personnel_number = self._current_row.employee_personnel_number

    def _restore_selection_context(self) -> bool:
        """Відновлює вибір після reload або зміни фільтрів.
        Restores selection after reload or filter changes.
        """

        restored = False
        if self._pending_record_id is not None:
            restored = self.registry_table.select_record(self._pending_record_id)
        if not restored and self._pending_personnel_number:
            restored = self.registry_table.select_employee(self._pending_personnel_number)
        self._pending_record_id = None
        self._pending_personnel_number = None
        return restored


def _row_matches(row: TrainingWorkspaceRow, values: dict[str, str]) -> bool:
    """Checks if row matches active filters."""

    haystack = " ".join(
        (
            row.employee_full_name,
            row.employee_personnel_number,
            row.department_name,
            row.site_name,
            row.position_name,
            row.conducted_by,
            row.training_type_label,
        )
    ).lower()
    if values["search"] and values["search"] not in haystack:
        return False
    if values["type"] and (row.training_type is None or row.training_type.value != values["type"]):
        return False
    if values["department"] and row.department_name != values["department"]:
        return False
    if values["site"] and row.site_name != values["site"]:
        return False
    if values["position"] and row.position_name != values["position"]:
        return False
    if values["status"] and row.status_filter.value != values["status"]:
        return False
    if values["conducted_by"] and row.conducted_by != values["conducted_by"]:
        return False
    if values["employee"] and row.employee_personnel_number != values["employee"]:
        return False
    if values["date_from"] and row.next_control_date not in {"", "-"} and row.next_control_date < values["date_from"]:
        return False
    if values["date_to"] and row.next_control_date not in {"", "-"} and row.next_control_date > values["date_to"]:
        return False
    return True


def _collapse_by_employee(rows: tuple[TrainingWorkspaceRow, ...]) -> tuple[TrainingWorkspaceRow, ...]:
    """Keeps one most-problematic summary row per employee."""

    priority = {
        TrainingRegistryFilter.INVALID: 5,
        TrainingRegistryFilter.MISSING: 4,
        TrainingRegistryFilter.OVERDUE: 3,
        TrainingRegistryFilter.WARNING: 2,
        TrainingRegistryFilter.CURRENT: 1,
        TrainingRegistryFilter.ALL: 0,
    }
    grouped: dict[str, list[TrainingWorkspaceRow]] = {}
    for row in rows:
        grouped.setdefault(row.employee_personnel_number, []).append(row)
    summarized_rows = [
        _build_employee_summary_row(employee_rows, priority)
        for employee_rows in grouped.values()
    ]
    return tuple(
        sorted(
            summarized_rows,
            key=lambda row: (-priority[row.status_filter], row.employee_full_name.lower(), row.record_id or 0),
        )
    )


def _build_employee_summary_row(
    employee_rows: list[TrainingWorkspaceRow],
    priority: dict[TrainingRegistryFilter, int],
) -> TrainingWorkspaceRow:
    """Builds a single employee row with the most severe current state."""

    anchor_row = min(
        employee_rows,
        key=lambda row: (-priority[row.status_filter], row.employee_full_name.lower(), row.record_id or 0),
    )
    return replace(
        anchor_row,
        training_type_label="Стан працівника",
        status_reason=_summarize_employee_row_reason(anchor_row),
    )


def _summarize_employee_row_reason(row: TrainingWorkspaceRow) -> str:
    """Builds one concise reason for the most severe employee training state."""

    reason_text = row.status_reason.replace("\n", " ").strip()
    if row.status_filter == TrainingRegistryFilter.INVALID:
        return f"{row.training_type_label}: {reason_text}"
    if row.status_filter == TrainingRegistryFilter.MISSING:
        return reason_text
    if row.status_filter == TrainingRegistryFilter.OVERDUE:
        return f"{row.training_type_label}: {reason_text}"
    if row.status_filter == TrainingRegistryFilter.WARNING:
        return f"{row.training_type_label}: {reason_text}"
    if not reason_text:
        return "Актуально: зауважень не виявлено."
    return f"Актуально: {reason_text}"
