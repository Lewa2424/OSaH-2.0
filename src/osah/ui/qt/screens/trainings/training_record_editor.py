from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.create_training_record import create_training_record
from osah.application.services.update_training_record import update_training_record
from osah.domain.entities.employee import Employee
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.format_training_work_risk_category_label import format_training_work_risk_category_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import SPACING


class TrainingRecordEditor(QWidget):
    """Форма створення і редагування одного запису інструктажу.
    Form for creating and editing one training record.
    """

    saved = Signal()

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self._database_path = database_path
        self._current_record_id: int | None = None
        self._is_updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        form = QFormLayout()
        self.employee_input = QComboBox()
        for employee in employees:
            if employee.employment_status.strip().lower() == "active":
                self.employee_input.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        form.addRow("Працівник", self.employee_input)

        self.type_input = QComboBox()
        for training_type in TrainingType:
            self.type_input.addItem(format_training_type_label(training_type), training_type.value)
        self.type_input.currentIndexChanged.connect(lambda _index: self._sync_scenario_fields())
        form.addRow("Тип", self.type_input)

        self.event_date_input = QLineEdit()
        self.event_date_input.setPlaceholderText("ДД.ММ.РРРР")
        self.event_date_input.textChanged.connect(lambda _text: self._sync_scenario_fields())
        form.addRow("Дата проведення", self.event_date_input)

        self.risk_label = QLabel("Категорія робіт")
        self.risk_input = QComboBox()
        for risk_category in (
            TrainingWorkRiskCategory.NOT_APPLICABLE,
            TrainingWorkRiskCategory.REGULAR,
            TrainingWorkRiskCategory.HIGH_RISK,
        ):
            self.risk_input.addItem(format_training_work_risk_category_label(risk_category), risk_category.value)
        self.risk_input.currentIndexChanged.connect(lambda _index: self._sync_scenario_fields())
        form.addRow(self.risk_label, self.risk_input)

        self.affects_repeated_input = QCheckBox("Перенести план повторного від дати цього інструктажу")
        self.affects_repeated_input.toggled.connect(lambda _checked: self._sync_scenario_fields())
        form.addRow("", self.affects_repeated_input)

        self.manual_date_input = QCheckBox("Ввести дату наступного контролю вручну")
        self.manual_date_input.toggled.connect(lambda _checked: self._sync_scenario_fields())
        form.addRow("", self.manual_date_input)

        self.next_date_label = QLabel("Наступний контроль")
        self.next_date_input = QLineEdit()
        self.next_date_input.setPlaceholderText("ДД.ММ.РРРР")
        form.addRow(self.next_date_label, self.next_date_input)

        self.conducted_by_input = QLineEdit()
        form.addRow("Проводив", self.conducted_by_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(80)
        form.addRow("Примітка", self.note_input)
        layout.addLayout(form)

        self.feedback_label = FormFeedbackLabel()
        layout.addWidget(self.feedback_label)

        self.save_button = QPushButton("Зберегти запис")
        self.save_button.setProperty("variant", "accent")
        self.save_button.clicked.connect(self._save_record)
        layout.addWidget(self.save_button)

        self.new_button = QPushButton("Новий запис")
        self.new_button.setProperty("variant", "secondary")
        self.new_button.clicked.connect(self.clear_form)
        layout.addWidget(self.new_button)
        self._sync_scenario_fields()

    def set_row(self, row: TrainingWorkspaceRow) -> None:
        """Заповнює форму вибраним записом або шаблоном для відсутнього запису.
        Fills the form with selected record or a template for a missing record.
        """

        self._is_updating = True
        self._current_record_id = row.record_id
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(row.employee_personnel_number)))
        if row.training_type:
            self.type_input.setCurrentIndex(max(0, self.type_input.findData(row.training_type.value)))
        self.event_date_input.setText("" if row.event_date == "-" else format_ui_date(row.event_date))
        self.next_date_input.setText("" if row.next_control_date == "-" else format_ui_date(row.next_control_date))
        self.risk_input.setCurrentIndex(max(0, self.risk_input.findData(row.work_risk_category.value)))
        self.affects_repeated_input.setChecked(
            row.training_type in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}
            and row.next_control_basis != TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL
        )
        self.manual_date_input.setChecked(row.next_control_basis == TrainingNextControlBasis.MANUAL)
        self.conducted_by_input.setText("" if row.conducted_by == "-" else row.conducted_by)
        self.note_input.setPlainText(row.note_text)
        self.save_button.setText("Створити запис" if row.is_missing else "Зберегти зміни")
        self._is_updating = False
        self._sync_scenario_fields(recalculate=False)

    def clear_form(self) -> None:
        """Готує форму до створення нового запису.
        Prepares the form for creating a new record.
        """

        self._is_updating = True
        self._current_record_id = None
        self.event_date_input.clear()
        self.next_date_input.clear()
        self.risk_input.setCurrentIndex(max(0, self.risk_input.findData(TrainingWorkRiskCategory.NOT_APPLICABLE.value)))
        self.affects_repeated_input.setChecked(False)
        self.manual_date_input.setChecked(False)
        self.conducted_by_input.clear()
        self.note_input.clear()
        self.save_button.setText("Створити запис")
        self._is_updating = False
        self._sync_scenario_fields()

    def _sync_scenario_fields(self, recalculate: bool = True) -> None:
        """Оновлює доступність полів за сценарієм вибраного типу інструктажу.
        Updates field availability for the selected training type scenario.
        """

        if self._is_updating:
            return

        training_type = TrainingType(str(self.type_input.currentData()))
        is_repeated_base = training_type in {TrainingType.PRIMARY, TrainingType.REPEATED}
        is_optional_transfer = training_type in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}
        should_transfer = is_repeated_base or (is_optional_transfer and self.affects_repeated_input.isChecked())

        self.affects_repeated_input.setVisible(is_optional_transfer)
        self.manual_date_input.setVisible(should_transfer)
        self.risk_label.setVisible(should_transfer)
        self.risk_input.setVisible(should_transfer)
        self.risk_input.setEnabled(should_transfer)
        self.next_date_label.setText("Первинний потрібен до" if training_type == TrainingType.INTRODUCTORY else "Наступний контроль")

        if should_transfer and self.risk_input.currentData() == TrainingWorkRiskCategory.NOT_APPLICABLE.value:
            self.risk_input.setCurrentIndex(max(0, self.risk_input.findData(TrainingWorkRiskCategory.REGULAR.value)))
            return
        if not should_transfer:
            self.risk_input.setCurrentIndex(max(0, self.risk_input.findData(TrainingWorkRiskCategory.NOT_APPLICABLE.value)))

        self.next_date_input.setReadOnly(not self.manual_date_input.isVisible() or not self.manual_date_input.isChecked())
        if not recalculate:
            return

        if training_type == TrainingType.INTRODUCTORY:
            self.next_date_input.setText(self.event_date_input.text().strip())
            return
        if not should_transfer:
            self.next_date_input.clear()
            return
        if self.manual_date_input.isChecked():
            return

        try:
            event_date = parse_ui_date_text(self.event_date_input.text())
            next_control_date, _, _ = resolve_training_next_control_date(
                training_type,
                event_date,
                TrainingWorkRiskCategory(str(self.risk_input.currentData())),
                None,
                self.affects_repeated_input.isChecked(),
                False,
            )
        except ValueError:
            self.next_date_input.clear()
            return
        self.next_date_input.setText(format_ui_date(next_control_date))

    def _save_record(self) -> None:
        """Зберігає запис через application service і повідомляє екран про оновлення.
        Saves the record through application service and notifies the screen to refresh.
        """

        training_type = TrainingType(str(self.type_input.currentData()))
        should_update_repeated_control = (
            training_type in {TrainingType.PRIMARY, TrainingType.REPEATED}
            or (
                training_type in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}
                and self.affects_repeated_input.isChecked()
            )
        )
        work_risk_category = (
            str(self.risk_input.currentData())
            if should_update_repeated_control
            else TrainingWorkRiskCategory.NOT_APPLICABLE.value
        )
        use_manual_next_control_date = self.manual_date_input.isVisible() and self.manual_date_input.isChecked()

        try:
            if self._current_record_id is None:
                create_training_record(
                    self._database_path,
                    str(self.employee_input.currentData()),
                    training_type.value,
                    self.event_date_input.text(),
                    self.next_date_input.text(),
                    self.conducted_by_input.text(),
                    self.note_input.toPlainText(),
                    work_risk_category,
                    should_update_repeated_control,
                    use_manual_next_control_date,
                )
            else:
                update_training_record(
                    self._database_path,
                    self._current_record_id,
                    str(self.employee_input.currentData()),
                    training_type.value,
                    self.event_date_input.text(),
                    self.next_date_input.text(),
                    self.conducted_by_input.text(),
                    self.note_input.toPlainText(),
                    work_risk_category,
                    should_update_repeated_control,
                    use_manual_next_control_date,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return

        self.feedback_label.show_success("Запис інструктажу збережено.")
        self.saved.emit()
