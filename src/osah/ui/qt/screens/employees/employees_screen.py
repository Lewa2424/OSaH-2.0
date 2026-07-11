from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QSplitter, QVBoxLayout, QWidget

from osah.application.services.archive_employee import archive_employee
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.domain.services.build_employee_topbar_summary import build_employee_topbar_summary
from osah.ui.qt.components.app_dialog import show_app_confirm_dialog
from osah.ui.qt.components.screen_states import EmptyStateWidget
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.employees.create_employee_dialog import CreateEmployeeDialog
from osah.ui.qt.screens.employees.edit_employee_dialog import EditEmployeeDialog
from osah.ui.qt.screens.employees.employee_details_pane import EmployeeDetailsPane
from osah.ui.qt.screens.employees.employee_registry_table import EmployeeRegistryTable
from osah.ui.qt.screens.employees.employees_filter_bar import EmployeesFilterBar
from osah.ui.qt.screens.employees.structure_tree_panel import StructureTreePanel


class EmployeesScreen(QWidget):
    """Full Qt screen for employees module. / Полный экран модуля работников."""

    module_navigation_requested = Signal(AppSection, str)
    module_record_navigation_requested = Signal(AppSection, str, int)

    def __init__(
        self,
        database_path: Path,
        workspace: EmployeeWorkspace,
        access_role: AccessRole,
        initial_personnel_number: str | None = None,
        initial_problem_key: str | None = None,
    ) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._read_only = access_role != AccessRole.INSPECTOR
        self._workspace = workspace
        self._initial_personnel_number = initial_personnel_number
        self._initial_problem_key = initial_problem_key
        self._visible_rows: tuple[EmployeeWorkspaceRow, ...] = workspace.rows

        self.setObjectName("employeesScreen")
        self.setStyleSheet(
            f"""
            QWidget#employeesScreen {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F4F7FB, stop:0.45 #EDF2F7, stop:1 #F8FBFD);
            }}
            QWidget#employeesScreen QSplitter::handle {{
                background: transparent;
            }}
            QWidget#employeesScreen QSplitter::handle:horizontal {{
                width: 10px;
            }}
            QWidget#employeesScreen QPushButton#employeesPrimaryAction {{
                min-height: 46px;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 800;
            }}
            QWidget#employeesScreen QWidget#employeesRightPanel {{
                background: transparent;
            }}
            """
        )

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
        splitter.addWidget(ScrollableTableFrame(self.registry_table))

        right_panel = QWidget()
        right_panel.setObjectName("employeesRightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(SPACING["sm"], 0, 0, 0)
        right_layout.setSpacing(SPACING["sm"])

        self._create_button = QPushButton("Додати працівника")
        self._create_button.setObjectName("employeesPrimaryAction")
        self._create_button.setProperty("variant", "accent")
        self._create_button.clicked.connect(self._open_create_employee_dialog)
        self._create_button.setVisible(not self._read_only)
        self._create_button.setEnabled(not self._read_only)
        right_layout.addWidget(self._create_button)

        self.details_pane = EmployeeDetailsPane(database_path=self._database_path, read_only=self._read_only)
        self.details_pane.edit_requested.connect(self._open_edit_employee_dialog)
        self.details_pane.archive_requested.connect(self._archive_employee)
        self.details_pane.module_navigation_requested.connect(self.module_navigation_requested.emit)
        self.details_pane.module_record_navigation_requested.connect(self.module_record_navigation_requested.emit)
        right_layout.addWidget(self.details_pane, stretch=1)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        layout.addWidget(splitter, stretch=1)

        self.empty_state = EmptyStateWidget()
        layout.addWidget(self.empty_state)

        self._apply_filters()
        self._focus_initial_employee()

    def focus_employee(self, personnel_number: str, problem_key: str | None = None) -> None:
        self._initial_personnel_number = personnel_number
        self._initial_problem_key = problem_key
        self.filter_bar.reset_filters()
        self.registry_table.select_employee(personnel_number)

    def topbar_summary(self):
        return build_employee_topbar_summary(self._workspace)

    def _apply_filters(self) -> None:
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

    def _apply_tree_intent(self, node_kind: str, node_value: str) -> None:
        if node_kind == "enterprise":
            self.filter_bar.reset_filters()
        elif node_kind == "department":
            self.filter_bar.set_department_filter(node_value)
        elif node_kind == "position":
            self.filter_bar.set_position_filter(node_value)

    def _show_employee(self, personnel_number: str) -> None:
        row = next((item for item in self._workspace.rows if item.employee.personnel_number == personnel_number), None)
        if row:
            self.details_pane.show_employee(row)

    def _focus_initial_employee(self) -> None:
        if self._initial_personnel_number:
            self.registry_table.select_employee(self._initial_personnel_number)

    def _open_create_employee_dialog(self) -> None:
        if self._read_only:
            return
        dialog = CreateEmployeeDialog(self._database_path, self._workspace, self._access_role, self)
        dialog.employee_created.connect(self._reload_workspace_after_create)
        dialog.exec()

    def _open_edit_employee_dialog(self, row: EmployeeWorkspaceRow) -> None:
        if self._read_only:
            return
        dialog = EditEmployeeDialog(self._database_path, self._workspace, row, self._access_role, self)
        dialog.employee_updated.connect(self._reload_workspace_after_create)
        dialog.exec()

    def _archive_employee(self, row: EmployeeWorkspaceRow) -> None:
        if show_app_confirm_dialog(
            self,
            "Підтвердження",
            f"Перемістити працівника «{row.employee.full_name}» в архів?",
            confirm_label="Архівувати",
            destructive=True,
        ):
            archive_employee(
                self._database_path,
                row.employee.personnel_number,
                access_role=self._access_role,
            )
            self._reload_workspace_after_create("")

    def _reload_workspace_after_create(self, personnel_number: str) -> None:
        self._workspace = load_employee_workspace(self._database_path)
        self.filter_bar.set_workspace(self._workspace)
        self.structure_tree.set_workspace(self._workspace)
        self._apply_filters()
        if personnel_number:
            self.registry_table.select_employee(personnel_number)


def _row_matches_filters(row: EmployeeWorkspaceRow, values: dict[str, object]) -> bool:
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
