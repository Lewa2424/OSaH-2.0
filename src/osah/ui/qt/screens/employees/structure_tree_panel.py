from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class StructureTreePanel(QWidget):
    """Left enterprise hierarchy panel for the employees module. / Левая панель организационной структуры."""

    node_selected = Signal(str, str)

    def __init__(self, workspace: EmployeeWorkspace) -> None:
        super().__init__()
        self._workspace = workspace
        self.setObjectName("structureTreePanel")
        self.setMinimumWidth(250)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, SPACING["md"], 0)
        layout.setSpacing(SPACING["sm"])

        self.setStyleSheet(
            f"""
            QWidget#structureTreePanel {{
                background: transparent;
            }}
            QWidget#structureTreePanel QLabel#treeTitle {{
                color: {COLOR['text_primary']};
                font-size: 21px;
                font-weight: 900;
            }}
            QWidget#structureTreePanel QLabel#treeSummary {{
                color: {COLOR['accent']};
                font-size: 13px;
                font-weight: 800;
            }}
            QWidget#structureTreePanel QLineEdit {{
                min-height: 40px;
                background: {COLOR['bg_card']};
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['lg']}px;
                padding: 0 14px;
            }}
            QWidget#structureTreePanel QTreeWidget {{
                background: {COLOR['bg_card']};
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['xl']}px;
                padding: 10px 8px;
            }}
            QWidget#structureTreePanel QTreeWidget::item {{
                height: 34px;
                padding: 4px 8px;
                margin: 1px 0;
                border-radius: 10px;
                color: {COLOR['text_primary']};
                font-size: 13px;
                font-weight: 700;
            }}
            QWidget#structureTreePanel QTreeWidget::item:hover {{
                background: {COLOR['hover_bg']};
            }}
            QWidget#structureTreePanel QTreeWidget::item:selected {{
                background: {COLOR['selection_bg']};
                color: {COLOR['text_primary']};
                border: 1px solid {COLOR['accent_soft']};
            }}
            """
        )

        title = QLabel("Організаційна структура")
        title.setObjectName("treeTitle")
        layout.addWidget(title)

        self._summary_label = QLabel()
        self._summary_label.setObjectName("treeSummary")
        layout.addWidget(self._summary_label)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Пошук підрозділу або посади")
        self._search_input.textChanged.connect(self._apply_search_filter)
        layout.addWidget(self._search_input)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(18)
        self.tree.setUniformRowHeights(False)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.itemSelectionChanged.connect(self._emit_selected_node)
        layout.addWidget(self.tree)
        self.refresh()

    def set_workspace(self, workspace: EmployeeWorkspace) -> None:
        """Updates tree data source and rebuilds nodes. / Обновляет источник данных дерева."""
        self._workspace = workspace
        self.refresh()

    def refresh(self) -> None:
        """Builds the enterprise-department-position tree. / Строит дерево предприятие-подразделение-должность."""

        self.tree.clear()
        root = self._build_tree_item(self._workspace.enterprise_name, self._workspace.rows)
        root.setData(0, 256, ("enterprise", ""))
        self.tree.addTopLevelItem(root)

        departments = sorted({row.department_name for row in self._workspace.rows})
        for department in departments:
            department_rows = tuple(row for row in self._workspace.rows if row.department_name == department)
            department_item = self._build_tree_item(department, department_rows)
            department_item.setData(0, 256, ("department", department))
            root.addChild(department_item)

            for position in sorted({row.position_name for row in department_rows}):
                position_rows = tuple(row for row in department_rows if row.position_name == position)
                position_item = self._build_tree_item(position, position_rows)
                position_item.setData(0, 256, ("position", position))
                department_item.addChild(position_item)

        self.tree.expandItem(root)
        self._summary_label.setText(f"{len(self._workspace.rows)} працівників • {len(departments)} підрозділів")
        self._apply_search_filter(self._search_input.text())

    def _emit_selected_node(self) -> None:
        """Emits selected node as a filter intent. / Передает выбранный узел как намерение фильтра."""

        selected = self.tree.selectedItems()
        if not selected:
            return
        node_kind, node_value = selected[0].data(0, 256)
        self.node_selected.emit(node_kind, node_value)

    def _format_node(self, name: str, rows: tuple) -> str:
        return f"{name} ({len(rows)})"

    def _build_tree_item(self, name: str, rows: tuple) -> QTreeWidgetItem:
        item = QTreeWidgetItem([self._format_node(name, rows)])
        item.setToolTip(0, f"{name}\nПрацівників: {len(rows)}")
        return item

    def _apply_search_filter(self, search_text: str) -> None:
        if self.tree.topLevelItemCount() == 0:
            return
        root = self.tree.topLevelItem(0)
        normalized_search_text = search_text.strip().lower()
        self._filter_item_recursive(root, normalized_search_text)
        if normalized_search_text:
            self.tree.expandAll()
        else:
            self.tree.collapseAll()
            self.tree.expandItem(root)

    def _filter_item_recursive(self, item: QTreeWidgetItem, normalized_search_text: str) -> bool:
        own_match = not normalized_search_text or normalized_search_text in item.text(0).lower()
        child_match = False
        for child_index in range(item.childCount()):
            child = item.child(child_index)
            child_visible = self._filter_item_recursive(child, normalized_search_text)
            child.setHidden(not child_visible)
            child_match = child_match or child_visible
        visible = own_match or child_match
        if item.parent() is None:
            item.setHidden(False)
            return True
        return visible
