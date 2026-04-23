from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.components.screen_states import EmptyStateWidget
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.employees.employee_details_pane import EmployeeDetailsPane
from osah.ui.qt.screens.employees.employee_registry_table import EmployeeRegistryTable
from osah.ui.qt.screens.employees.employees_filter_bar import EmployeesFilterBar
from osah.ui.qt.screens.employees.structure_tree_panel import StructureTreePanel


class EmployeesScreen(QWidget):
    """Full Qt screen for employees module."""

    def __init__(
        self,
        workspace: EmployeeWorkspace,
        initial_personnel_number: str | None = None,
        initial_problem_key: str | None = None,
    ) -> None:
        super().__init__()
        self._workspace = workspace
        self._initial_personnel_number = initial_personnel_number
        self._initial_problem_key = initial_problem_key
        self._visible_rows: tuple[EmployeeWorkspaceRow, ...] = workspace.rows

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        subtitle_text = "Реєстр персоналу з ієрархією, пошуком, фільтрами і ОП-карткою працівника."
        if initial_personnel_number:
            subtitle_text = f"Перехід із сигналу: відкрито працівника {initial_personnel_number}."
        self._section_header = SectionHeader("Працівники", subtitle_text)
        self._section_header.set_warning_accent(bool(initial_personnel_number))
        layout.addWidget(self._section_header)

        self.filter_bar = EmployeesFilterBar(workspace)
        self.filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self.filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.structure_tree = StructureTreePanel(workspace)
        self.structure_tree.node_selected.connect(self._apply_tree_intent)
        splitter.addWidget(self.structure_tree)

        self.registry_table = EmployeeRegistryTable()
        self.registry_table.employee_selected.connect(self._show_employee)
        splitter.addWidget(self.registry_table)

        self.details_pane = EmployeeDetailsPane()
        splitter.addWidget(self.details_pane)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        layout.addWidget(splitter, stretch=1)

        self.empty_state = EmptyStateWidget()
        layout.addWidget(self.empty_state)

        self._apply_filters()
        self._focus_initial_employee()

    # ###### ФОКУС НА ПРАЦІВНИКУ / FOCUS EMPLOYEE ######
    def focus_employee(self, personnel_number: str, problem_key: str | None = None) -> None:
        """Opens employee card from dashboard navigation intent."""

        self._initial_personnel_number = personnel_number
        self._initial_problem_key = problem_key
        self.filter_bar.reset_filters()
        self.registry_table.select_employee(personnel_number)

    # ###### ЗАСТОСУВАННЯ ФІЛЬТРІВ / APPLY FILTERS ######
    def _apply_filters(self) -> None:
        """Combines search, tree and filters without domain recalculations."""

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches_filters(row, values))
        self._visible_rows = rows
        self.registry_table.set_rows(rows)
        if rows:
            self.empty_state.hide()
            self.registry_table.selectRow(0)
        else:
            self.empty_state.show_state(
                "Немає працівників за поточними фільтрами.",
                "Скиньте фільтри або змініть умови пошуку.",
            )
            self.details_pane.show_empty_state()

    # ###### НАМІР З ДЕРЕВА / APPLY TREE INTENT ######
    def _apply_tree_intent(self, node_kind: str, node_value: str) -> None:
        """Converts structure tree selection into registry filters."""

        if node_kind == "enterprise":
            self.filter_bar.reset_filters()
        elif node_kind == "department":
            self.filter_bar.set_department_filter(node_value)
        elif node_kind == "position":
            self.filter_bar.set_position_filter(node_value)

    # ###### ПОКАЗ ПРАЦІВНИКА / SHOW EMPLOYEE ######
    def _show_employee(self, personnel_number: str) -> None:
        """Shows selected employee in right details pane."""

        row = next((item for item in self._workspace.rows if item.employee.personnel_number == personnel_number), None)
        if row:
            self.details_pane.show_employee(row)

    # ###### ПОЧАТКОВИЙ ФОКУС / INITIAL FOCUS ######
    def _focus_initial_employee(self) -> None:
        """Applies initial focus from navigation intent when provided."""

        if self._initial_personnel_number:
            self.registry_table.select_employee(self._initial_personnel_number)


# ###### ПЕРЕВІРКА ФІЛЬТРІВ / FILTER MATCH ######
def _row_matches_filters(row: EmployeeWorkspaceRow, values: dict[str, object]) -> bool:
    """Checks whether employee row matches active filters."""

    search = str(values["search"])
    haystack = " ".join(
        [
            row.employee.full_name,
            row.employee.personnel_number,
            row.position_name,
            row.department_name,
            row.site_name,
        ]
    ).lower()
    if search and search not in haystack:
        return False

    if values["department"] and row.department_name != values["department"]:
        return False
    if values["position"] and row.position_name != values["position"]:
        return False
    if values["status"] and row.status_level.value != values["status"]:
        return False
    if values["critical_only"] and row.status_level != EmployeeStatusLevel.CRITICAL:
        return False
    if values["warning_only"] and row.status_level != EmployeeStatusLevel.WARNING:
        return False

    return True
