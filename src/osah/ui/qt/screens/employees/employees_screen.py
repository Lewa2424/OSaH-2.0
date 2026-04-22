from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.employees.employee_details_pane import EmployeeDetailsPane
from osah.ui.qt.screens.employees.employee_registry_table import EmployeeRegistryTable
from osah.ui.qt.screens.employees.employees_filter_bar import EmployeesFilterBar
from osah.ui.qt.screens.employees.structure_tree_panel import StructureTreePanel


class EmployeesScreen(QWidget):
    """Повноцінний Qt-екран модуля працівників.
    Full Qt screen for the employees module.
    """

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

        title = QLabel("Працівники")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)

        subtitle_text = "Реєстр персоналу з ієрархією, пошуком, фільтрами та ОП-карткою працівника."
        if initial_personnel_number:
            subtitle_text = f"Перехід із сигналу: відкрито працівника {initial_personnel_number}."
        subtitle = QLabel(subtitle_text)
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

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

        self.empty_state = QLabel("")
        self.empty_state.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(self.empty_state)

        self._apply_filters()
        self._focus_initial_employee()

    # ###### ФОКУС НА ПРАЦІВНИКУ / FOCUS EMPLOYEE ######
    def focus_employee(self, personnel_number: str, problem_key: str | None = None) -> None:
        """Відкриває працівника за навігаційним наміром dashboard -> employees -> card.
        Opens an employee from a navigation intent dashboard -> employees -> card.
        """

        self._initial_personnel_number = personnel_number
        self._initial_problem_key = problem_key
        self.filter_bar.reset_filters()
        self.registry_table.select_employee(personnel_number)

    # ###### ЗАСТОСУВАННЯ ФІЛЬТРІВ / APPLY FILTERS ######
    def _apply_filters(self) -> None:
        """Комбінує пошук, дерево і фільтри без перерахунку доменних статусів.
        Combines search, tree and filters without recalculating domain statuses.
        """

        values = self.filter_bar.values()
        rows = tuple(row for row in self._workspace.rows if _row_matches_filters(row, values))
        self._visible_rows = rows
        self.registry_table.set_rows(rows)
        self.empty_state.setText("" if rows else "Нічого не знайдено. Змініть пошук або скиньте фільтри.")
        if rows:
            self.registry_table.selectRow(0)
        else:
            self.details_pane.show_empty_state()

    # ###### НАМІР З ДЕРЕВА / TREE INTENT ######
    def _apply_tree_intent(self, node_kind: str, node_value: str) -> None:
        """Перетворює вибір у дереві на активні фільтри реєстру.
        Converts tree selection into active registry filters.
        """

        if node_kind == "enterprise":
            self.filter_bar.reset_filters()
        elif node_kind == "department":
            self.filter_bar.set_department_filter(node_value)
        elif node_kind == "position":
            self.filter_bar.set_position_filter(node_value)

    # ###### ПОКАЗ ПРАЦІВНИКА / SHOW EMPLOYEE ######
    def _show_employee(self, personnel_number: str) -> None:
        """Показує праву картку вибраного працівника.
        Shows the right detail card for the selected employee.
        """

        row = next((item for item in self._workspace.rows if item.employee.personnel_number == personnel_number), None)
        if row:
            self.details_pane.show_employee(row)

    def _focus_initial_employee(self) -> None:
        """Виконує первинний фокус за навігаційним наміром, якщо він заданий.
        Applies initial focus from navigation intent when provided.
        """

        if self._initial_personnel_number:
            self.registry_table.select_employee(self._initial_personnel_number)


# ###### ПЕРЕВІРКА ФІЛЬТРІВ / FILTER MATCH ######
def _row_matches_filters(row: EmployeeWorkspaceRow, values: dict[str, object]) -> bool:
    """Перевіряє, чи рядок працівника відповідає активним фільтрам.
    Checks whether an employee row matches active filters.
    """

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
