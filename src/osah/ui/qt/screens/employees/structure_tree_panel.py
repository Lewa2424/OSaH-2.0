from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.domain.services.rank_employee_status_level import rank_employee_status_level
from osah.ui.qt.design.tokens import COLOR, SPACING


class StructureTreePanel(QWidget):
    """Ліва панель ієрархії підприємства для модуля працівників.
    Left enterprise hierarchy panel for the employees module.
    """

    node_selected = Signal(str, str)
    create_employee_requested = Signal()

    def __init__(self, workspace: EmployeeWorkspace) -> None:
        super().__init__()
        self._workspace = workspace
        self.setMinimumWidth(250)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, SPACING["md"], 0)
        layout.setSpacing(SPACING["sm"])

        create_button = QPushButton("Додати працівника")
        create_button.setProperty("variant", "accent")
        create_button.clicked.connect(self.create_employee_requested.emit)
        layout.addWidget(create_button)

        title = QLabel("Структура")
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        layout.addWidget(title)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self._emit_selected_node)
        layout.addWidget(self.tree)
        self.refresh()

    # ###### ОНОВЛЕННЯ WORKSPACE / UPDATE WORKSPACE ######
    def set_workspace(self, workspace: EmployeeWorkspace) -> None:
        """Оновлює джерело даних дерева і перебудовує вузли.
        Updates tree data source and rebuilds nodes.
        """

        self._workspace = workspace
        self.refresh()

    # ###### ОНОВЛЕННЯ ДЕРЕВА / REFRESH TREE ######
    def refresh(self) -> None:
        """Будує дерево підприємство-підрозділ-посада з проблемними лічильниками.
        Builds the enterprise-department-position tree with problem counters.
        """

        self.tree.clear()
        root = QTreeWidgetItem([self._format_node(self._workspace.enterprise_name, self._workspace.rows)])
        root.setData(0, 256, ("enterprise", ""))
        self.tree.addTopLevelItem(root)

        departments = sorted({row.department_name for row in self._workspace.rows})
        for department in departments:
            department_rows = tuple(row for row in self._workspace.rows if row.department_name == department)
            department_item = QTreeWidgetItem([self._format_node(department, department_rows)])
            department_item.setData(0, 256, ("department", department))
            root.addChild(department_item)

            for position in sorted({row.position_name for row in department_rows}):
                position_rows = tuple(row for row in department_rows if row.position_name == position)
                position_item = QTreeWidgetItem([self._format_node(position, position_rows)])
                position_item.setData(0, 256, ("position", position))
                department_item.addChild(position_item)

        self.tree.expandItem(root)

    # ###### ВИБІР ВУЗЛА / SELECT NODE ######
    def _emit_selected_node(self) -> None:
        """Передає вибраний вузол екрана як тип і значення фільтра.
        Emits selected node as filter type and value.
        """

        selected = self.tree.selectedItems()
        if not selected:
            return
        node_kind, node_value = selected[0].data(0, 256)
        self.node_selected.emit(node_kind, node_value)

    # ###### ПІДПИС ВУЗЛА / NODE LABEL ######
    def _format_node(self, name: str, rows: tuple) -> str:
        """Формує текст вузла з кількістю працівників.
        Builds node text with employee count.
        """

        return f"{name} ({len(rows)})"
