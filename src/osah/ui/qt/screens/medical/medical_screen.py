from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_medical_workspace import load_medical_workspace
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.medical_workspace import MedicalWorkspace
from osah.domain.entities.medical_workspace_mode import MedicalWorkspaceMode
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.medical.medical_filter_bar import MedicalFilterBar
from osah.ui.qt.screens.medical.medical_record_details_pane import MedicalRecordDetailsPane
from osah.ui.qt.screens.medical.medical_registry_table import MedicalRegistryTable
from osah.ui.qt.screens.medical.medical_summary_panel import MedicalSummaryPanel


class MedicalScreen(QWidget):
    """Повноцінний Qt-екран модуля медицини і меддопусків.
    Full Qt screen for medical admission and restriction control.
    """

    employee_open_requested = Signal(str)

    def __init__(self, database_path: Path, workspace: MedicalWorkspace, initial_status: str | None = None) -> None:
        super().__init__()
        self._database_path = database_path
        self._workspace = workspace

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Медицина")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)
        subtitle = QLabel("Контроль меддопуску, строків дії та робочих обмежень без зберігання діагнозів.")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        self.summary_panel = MedicalSummaryPanel(workspace.summary)
        layout.addWidget(self.summary_panel)
        self.filter_bar = MedicalFilterBar(workspace)
        self.filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self.filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.registry_table = MedicalRegistryTable()
        self.registry_table.row_selected.connect(self._show_row)
        splitter.addWidget(self.registry_table)

        self.details_pane = MedicalRecordDetailsPane(database_path, workspace.employees)
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
        """Перезавантажує дані після створення або редагування медичного запису.
        Reloads data after creating or editing a medical record.
        """

        self._workspace = load_medical_workspace(self._database_path)
        self.summary_panel.set_summary(self._workspace.summary)
        self._apply_filters()

    # ###### ЗАСТОСУВАННЯ ФІЛЬТРІВ / APPLY FILTERS ######
    def _apply_filters(self) -> None:
        """Застосовує комбіновані фільтри без доменних розрахунків у UI.
        Applies combined filters without domain calculations in UI.
        """

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches(row, values))
        if values["mode"] == MedicalWorkspaceMode.BY_EMPLOYEES.value:
            rows = _collapse_by_employee(rows)
        self.registry_table.set_rows(rows)
        self.empty_state.setText("" if rows else "Нічого не знайдено. Змініть фільтри або скиньте пошук.")
        self.registry_table.select_first()

    # ###### ПОКАЗ РЯДКА / SHOW ROW ######
    def _show_row(self, row: MedicalWorkspaceRow) -> None:
        """Показує вибраний медичний запис у правій панелі.
        Shows the selected medical record in the right pane.
        """

        self.details_pane.show_row(row)

    # ###### СТАРТОВИЙ ФІЛЬТР / INITIAL FILTER ######
    def _apply_initial_status(self, initial_status: str) -> None:
        """Активує стартовий фільтр статусу з navigation intent.
        Activates initial status filter from navigation intent.
        """

        try:
            self.filter_bar.set_status_filter(MedicalStatus(initial_status))
        except ValueError:
            return


# ###### ПЕРЕВІРКА ФІЛЬТРІВ / FILTER MATCH ######
def _row_matches(row: MedicalWorkspaceRow, values: dict[str, str | bool]) -> bool:
    """Перевіряє відповідність рядка активним фільтрам екрана.
    Checks whether a row matches active screen filters.
    """

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
    """Залишає для кожного працівника найпроблемніший медичний рядок.
    Keeps the most problematic medical row for each employee.
    """

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
