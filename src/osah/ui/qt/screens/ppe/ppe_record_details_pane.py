from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.domain.entities.employee import Employee
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.services.build_ppe_workspace_rows import build_ppe_workspace_rows
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.ppe.ppe_record_editor import PpeRecordEditor


class PpeRecordDetailsPane(QScrollArea):
    """Права панель картки ЗІЗ працівника.
    Right employee PPE-card pane.
    """

    employee_requested = Signal(str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...], ppe_names: tuple[str, ...]) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumWidth(360)
        self._database_path = database_path
        self._employees_by_number = {employee.personnel_number: employee for employee in employees}
        self._current_personnel_number: str | None = None
        self._row_lookup: dict[int, PpeWorkspaceRow] = {}
        self.editor = PpeRecordEditor(database_path, employees, ppe_names)
        self.open_employee_button = QPushButton("Відкрити картку працівника")
        self.open_employee_button.setProperty("variant", "secondary")
        self.open_employee_button.clicked.connect(self._emit_employee_request)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        self.title = QLabel("Картка ЗІЗ")
        self.title.setStyleSheet("font-size: 15px; font-weight: 900;")
        layout.addWidget(self.title)

        self.employee_name_label = QLabel("Оберіть працівника у реєстрі.")
        self.employee_name_label.setWordWrap(True)
        self.employee_name_label.setStyleSheet(
            f"color: {COLOR['text_secondary']}; font-size: 15px; font-weight: 900;"
        )
        layout.addWidget(self.employee_name_label)

        self.selector_label = QLabel("Виберіть відображувану позицію ЗІЗ")
        self.selector_label.setStyleSheet("font-weight: 800;")
        layout.addWidget(self.selector_label)

        self.ppe_selector = QComboBox()
        self.ppe_selector.currentIndexChanged.connect(self._apply_selector_choice)
        layout.addWidget(self.ppe_selector)

        self.editor_section_label = QLabel("Дані ЗІЗ та редагування")
        self.editor_section_label.setStyleSheet("font-weight: 800;")
        layout.addWidget(self.editor_section_label)

        layout.addWidget(self.editor)
        layout.addWidget(self.open_employee_button)
        layout.addStretch()
        self.setWidget(container)
        self.show_empty_state()

    def show_empty_state(self) -> None:
        """Показує порожній стан картки без вибраного працівника.
        Shows the empty card state without a selected employee.
        """

        self._current_personnel_number = None
        self._row_lookup = {}
        self.employee_name_label.setText("Оберіть працівника у реєстрі.")
        self.ppe_selector.blockSignals(True)
        self.ppe_selector.clear()
        self.ppe_selector.setEnabled(False)
        self.ppe_selector.blockSignals(False)
        self.open_employee_button.setEnabled(False)
        self.editor.setEnabled(False)
        self.editor.clear_form()

    def show_row(self, row: PpeWorkspaceRow) -> None:
        """Відкриває картку ЗІЗ вибраного працівника.
        Opens the employee PPE card for the selected row.
        """

        employee = self._employees_by_number.get(row.employee_personnel_number)
        if employee is None:
            self.show_empty_state()
            return

        self._current_personnel_number = employee.personnel_number
        self.employee_name_label.setText(f"{employee.full_name} ({employee.personnel_number})")
        self.open_employee_button.setEnabled(True)
        self.editor.setEnabled(True)
        self.editor.set_locked_employee(employee.personnel_number)

        employee_rows = tuple(
            item
            for item in build_ppe_workspace_rows((employee,), load_ppe_registry(self._database_path))
            if item.employee_personnel_number == employee.personnel_number
        )
        self._row_lookup = {
            int(employee_row.record_id): employee_row
            for employee_row in employee_rows
            if employee_row.record_id is not None
        }
        self._rebuild_selector(employee_rows, row)

    def _rebuild_selector(
        self,
        employee_rows: tuple[PpeWorkspaceRow, ...],
        selected_row: PpeWorkspaceRow,
    ) -> None:
        self.ppe_selector.blockSignals(True)
        self.ppe_selector.clear()
        for employee_row in sorted(employee_rows, key=lambda item: (item.ppe_name.lower(), item.record_id or 0)):
            self.ppe_selector.addItem(
                f"{employee_row.ppe_name} — {format_ui_date(employee_row.replacement_date)}",
                ("existing", int(employee_row.record_id)),
            )
        self.ppe_selector.addItem("+ Створити нову позицію ЗІЗ", ("create_new", ""))
        self._style_action_item(self.ppe_selector, self.ppe_selector.count() - 1)
        self.ppe_selector.setEnabled(True)
        self.ppe_selector.blockSignals(False)
        self._select_initial_item(selected_row)

    def _select_initial_item(self, selected_row: PpeWorkspaceRow) -> None:
        target_mode = "create_new"
        target_value = ""
        if selected_row.record_id is not None:
            target_mode = "existing"
            target_value = int(selected_row.record_id)

        for index in range(self.ppe_selector.count()):
            item_data = self.ppe_selector.itemData(index)
            if not isinstance(item_data, tuple) or len(item_data) != 2:
                continue
            if item_data[0] == target_mode and item_data[1] == target_value:
                self.ppe_selector.setCurrentIndex(index)
                self._apply_selector_choice(index)
                return
        self.ppe_selector.setCurrentIndex(0)
        self._apply_selector_choice(0)

    def _apply_selector_choice(self, index: int) -> None:
        item_data = self.ppe_selector.itemData(index)
        if self._current_personnel_number is None or not isinstance(item_data, tuple) or len(item_data) != 2:
            return
        mode, value = item_data
        if mode == "existing":
            row = self._row_lookup.get(int(value))
            if row is not None:
                self.editor.set_row(row)
            return
        self.editor.prepare_card_create_mode(self._current_personnel_number)

    def _emit_employee_request(self) -> None:
        """Передає запит відкрити картку працівника.
        Emits a request to open the employee card.
        """

        if self._current_personnel_number:
            self.employee_requested.emit(self._current_personnel_number)

    def _style_action_item(self, combo_box: QComboBox, index: int) -> None:
        """Виділяє сервісний пункт вибору як дію створення.
        Highlights the service selector item as a creation action.
        """

        combo_box.setItemData(index, QColor(COLOR["accent"]), Qt.ItemDataRole.ForegroundRole)
        action_font = QFont()
        action_font.setBold(True)
        combo_box.setItemData(index, action_font, Qt.ItemDataRole.FontRole)
