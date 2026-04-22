from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_training_workspace import load_training_workspace
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_workspace import TrainingWorkspace
from osah.domain.entities.training_workspace_mode import TrainingWorkspaceMode
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.trainings.training_quick_stats import TrainingQuickStats
from osah.ui.qt.screens.trainings.training_record_details_pane import TrainingRecordDetailsPane
from osah.ui.qt.screens.trainings.training_summary_panel import TrainingSummaryPanel
from osah.ui.qt.screens.trainings.trainings_filter_bar import TrainingsFilterBar
from osah.ui.qt.screens.trainings.trainings_registry_table import TrainingsRegistryTable


class TrainingsScreen(QWidget):
    """Повноцінний Qt-екран модуля інструктажів.
    Full Qt screen for the trainings module.
    """

    employee_open_requested = Signal(str)

    def __init__(self, database_path: Path, workspace: TrainingWorkspace, initial_status: str | None = None) -> None:
        super().__init__()
        self._database_path = database_path
        self._workspace = workspace
        self._visible_rows: tuple[TrainingWorkspaceRow, ...] = workspace.rows

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Інструктажі")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)

        subtitle = QLabel("Контроль строків, просрочок, відсутніх записів і відповідальних за інструктажі.")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

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
        self.summary_panel = TrainingSummaryPanel()
        center_layout.addWidget(self.summary_panel)
        self.registry_table = TrainingsRegistryTable()
        self.registry_table.row_selected.connect(self._show_row)
        center_layout.addWidget(self.registry_table, stretch=1)
        splitter.addWidget(center)

        self.details_pane = TrainingRecordDetailsPane(database_path, workspace.employees)
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
        """Перезавантажує дані після створення або редагування запису.
        Reloads data after creating or editing a record.
        """

        self._workspace = load_training_workspace(self._database_path)
        self.quick_stats.set_summary(self._workspace.summary)
        self._apply_filters()

    # ###### ЗАСТОСУВАННЯ ФІЛЬТРІВ / APPLY FILTERS ######
    def _apply_filters(self) -> None:
        """Застосовує комбіновані фільтри без доменних розрахунків у UI.
        Applies combined filters without domain calculations in UI.
        """

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches(row, values))
        if values["mode"] == TrainingWorkspaceMode.BY_EMPLOYEES.value:
            rows = _collapse_by_employee(rows)
        self._visible_rows = rows
        self.registry_table.set_rows(rows)
        self.empty_state.setText("" if rows else "Нічого не знайдено. Змініть фільтри або скиньте пошук.")
        self.registry_table.select_first()

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def _show_row(self, row: TrainingWorkspaceRow) -> None:
        """Показує вибраний запис у правій панелі і короткому підсумку.
        Shows the selected record in the right pane and summary panel.
        """

        self.summary_panel.set_row(row)
        self.details_pane.show_row(row)

    def _apply_initial_status(self, initial_status: str) -> None:
        """Активує стартовий фільтр статусу з navigation intent.
        Activates initial status filter from navigation intent.
        """

        try:
            self.filter_bar.set_status_filter(TrainingRegistryFilter(initial_status))
        except ValueError:
            return


# ###### ПЕРЕВІРКА ФІЛЬТРІВ / FILTER MATCH ######
def _row_matches(row: TrainingWorkspaceRow, values: dict[str, str]) -> bool:
    """Перевіряє відповідність рядка активним фільтрам екрана.
    Checks if a row matches active screen filters.
    """

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
    if values["date_from"] and row.next_control_date != "-" and row.next_control_date < values["date_from"]:
        return False
    if values["date_to"] and row.next_control_date != "-" and row.next_control_date > values["date_to"]:
        return False
    return True


def _collapse_by_employee(rows: tuple[TrainingWorkspaceRow, ...]) -> tuple[TrainingWorkspaceRow, ...]:
    """Залишає для кожного працівника найпроблемніший рядок інструктажів.
    Keeps the most problematic training row for each employee.
    """

    priority = {
        TrainingRegistryFilter.MISSING: 4,
        TrainingRegistryFilter.OVERDUE: 3,
        TrainingRegistryFilter.WARNING: 2,
        TrainingRegistryFilter.CURRENT: 1,
        TrainingRegistryFilter.ALL: 0,
    }
    selected: dict[str, TrainingWorkspaceRow] = {}
    for row in rows:
        current = selected.get(row.employee_personnel_number)
        if current is None or priority[row.status_filter] > priority[current.status_filter]:
            selected[row.employee_personnel_number] = row
    return tuple(selected.values())
