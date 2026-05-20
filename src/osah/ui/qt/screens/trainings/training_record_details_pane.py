from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from osah.application.services.load_training_registry import load_training_registry
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.employee import Employee
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.build_training_workspace_rows import build_training_workspace_rows
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.trainings.training_record_editor import TrainingRecordEditor


class TrainingRecordDetailsPane(QScrollArea):
    """Права панель картки інструктажів працівника.
    Right employee training-card pane.
    """

    employee_requested = Signal(str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...], access_role: AccessRole) -> None:
        super().__init__()
        self._read_only = access_role != AccessRole.INSPECTOR
        self.setWidgetResizable(True)
        self.setMinimumWidth(360)
        self._database_path = database_path
        self._employees_by_number = {employee.personnel_number: employee for employee in employees}
        self._current_personnel_number: str | None = None
        self._row_lookup: dict[int, TrainingWorkspaceRow] = {}
        self.editor = TrainingRecordEditor(database_path, employees, access_role)
        self.open_employee_button = QPushButton("Відкрити картку працівника")
        self.open_employee_button.setProperty("variant", "secondary")
        self.open_employee_button.clicked.connect(self._emit_employee_request)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        self.title = QLabel("Картка інструктажів")
        self.title.setStyleSheet("font-size: 15px; font-weight: 900;")
        layout.addWidget(self.title)

        self.employee_name_label = QLabel("Оберіть працівника у реєстрі.")
        self.employee_name_label.setWordWrap(True)
        self.employee_name_label.setStyleSheet(
            f"color: {COLOR['text_secondary']}; font-size: 15px; font-weight: 900;"
        )
        layout.addWidget(self.employee_name_label)

        self.selector_label = QLabel("Виберіть відображуваний тип інструктажу")
        self.selector_label.setStyleSheet("font-weight: 800;")
        layout.addWidget(self.selector_label)

        self.training_selector = QComboBox()
        self.training_selector.currentIndexChanged.connect(self._apply_selector_choice)
        layout.addWidget(self.training_selector)

        self.editor_section_label = QLabel("Дані інструктажу та редагування")
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
        self.training_selector.blockSignals(True)
        self.training_selector.clear()
        self.training_selector.setEnabled(False)
        self.training_selector.blockSignals(False)
        self.open_employee_button.setEnabled(False)
        self.editor.setEnabled(False)
        self.editor.clear_form()
        self.editor.set_type_locked(False)

    def show_row(self, row: TrainingWorkspaceRow) -> None:
        """Відкриває картку інструктажів вибраного працівника.
        Opens the employee training card for the selected row.
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

        current_records = tuple(
            record
            for record in load_training_registry(self._database_path)
            if record.employee_personnel_number == employee.personnel_number
        )
        employee_rows = build_training_workspace_rows((employee,), current_records)
        self._row_lookup = {
            int(employee_row.record_id): employee_row
            for employee_row in employee_rows
            if employee_row.record_id is not None
        }
        self._rebuild_selector(employee_rows, row)

    def _rebuild_selector(
        self,
        employee_rows: tuple[TrainingWorkspaceRow, ...],
        selected_row: TrainingWorkspaceRow,
    ) -> None:
        self.training_selector.blockSignals(True)
        self.training_selector.clear()
        row_by_type = {
            row.training_type: row
            for row in employee_rows
            if row.training_type is not None and not row.is_missing and row.training_type != TrainingType.TARGETED
        }
        missing_primary_row = next(
            (row for row in employee_rows if row.is_missing and row.training_type == TrainingType.PRIMARY),
            None,
        )
        targeted_rows = tuple(
            sorted(
                (row for row in employee_rows if row.training_type == TrainingType.TARGETED and not row.is_missing),
                key=lambda item: (item.event_date, item.record_id or 0),
                reverse=True,
            )
        )

        for training_type in (
            TrainingType.INTRODUCTORY,
            TrainingType.PRIMARY,
            TrainingType.REPEATED,
            TrainingType.UNSCHEDULED,
        ):
            training_row = row_by_type.get(training_type)
            if training_row is not None:
                self.training_selector.addItem(
                    f"{format_training_type_label(training_type)} — {format_ui_date(training_row.event_date)}",
                    ("existing", int(training_row.record_id)),
                )
                continue
            if training_type == TrainingType.PRIMARY and missing_primary_row is not None:
                self.training_selector.addItem(
                    f"{format_training_type_label(training_type)} — не створено",
                    ("missing", training_type.value),
                )
                continue
            self.training_selector.addItem(
                f"{format_training_type_label(training_type)} — не створено",
                ("missing", training_type.value),
            )

        if targeted_rows:
            for targeted_row in targeted_rows:
                label = f"Цільовий — {format_ui_date(targeted_row.event_date)}"
                target_row = self._row_lookup.get(int(targeted_row.record_id or 0))
                if target_row and target_row.basis_text:
                    label = f"{label} ({target_row.basis_text})"
                self.training_selector.addItem(label, ("existing", int(targeted_row.record_id)))
        else:
            self.training_selector.addItem("Цільовий — не створено", ("missing", TrainingType.TARGETED.value))

        if not self._read_only:
            self.training_selector.addItem("+ Створити новий інструктаж", ("create_new", ""))
            self._style_action_item(self.training_selector, self.training_selector.count() - 1)
        self.training_selector.setEnabled(True)
        self.training_selector.blockSignals(False)
        self._select_initial_item(selected_row)

    def _select_initial_item(self, selected_row: TrainingWorkspaceRow) -> None:
        target_mode = "create_new"
        target_value = ""
        if selected_row.record_id is not None:
            target_mode = "existing"
            target_value = int(selected_row.record_id)
        elif selected_row.training_type is not None:
            target_mode = "missing"
            target_value = selected_row.training_type.value

        for index in range(self.training_selector.count()):
            item_data = self.training_selector.itemData(index)
            if not isinstance(item_data, tuple) or len(item_data) != 2:
                continue
            if item_data[0] == target_mode and item_data[1] == target_value:
                self.training_selector.setCurrentIndex(index)
                self._apply_selector_choice(index)
                return
        self.training_selector.setCurrentIndex(0)
        self._apply_selector_choice(0)

    def _apply_selector_choice(self, index: int) -> None:
        item_data = self.training_selector.itemData(index)
        if self._current_personnel_number is None or not isinstance(item_data, tuple) or len(item_data) != 2:
            return
        mode, value = item_data
        if mode == "existing":
            row = self._row_lookup.get(int(value))
            if row is not None:
                self.editor.show_card_row(row, lock_type=True)
            return
        if mode == "missing":
            self.editor.prepare_card_create_mode(
                self._current_personnel_number,
                TrainingType(str(value)),
                lock_type=True,
            )
            return
        self.editor.prepare_card_create_mode(self._current_personnel_number, None, lock_type=False)

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
