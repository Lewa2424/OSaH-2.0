from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.create_training_record import create_training_record
from osah.application.services.delete_training_record import delete_training_record
from osah.application.services.update_training_record import update_training_record
from osah.domain.entities.employee import Employee
from osah.domain.entities.training_knowledge_check_result import TrainingKnowledgeCheckResult
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_admission_status import TrainingWorkAdmissionStatus
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.build_default_primary_requirement_for_person_category import (
    build_default_primary_requirement_for_person_category,
)
from osah.domain.services.format_training_person_category_label import format_training_person_category_label
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.format_training_work_risk_category_label import format_training_work_risk_category_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date
from osah.ui.qt.components.basis_note_panel import BasisNotePanel
from osah.ui.qt.components.date_line_edit import DateLineEdit
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.info_tooltip_icon import InfoTooltipIcon
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.hints.normative_hints import (
    TRAINING_KNOWLEDGE_CHECK_HINT,
    TRAINING_REPEAT_PERIOD_HINT,
    TRAINING_TARGET_HINT,
    TRAINING_TYPE_HINT,
)


class TrainingRecordEditor(QWidget):
    """Форма создания и редактирования одного записи инструктажа.
    Form for creating and editing one training record.
    """

    saved = Signal()
    deleted = Signal()

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
        form.addRow(self._with_info("Тип", TRAINING_TYPE_HINT), self.type_input)

        self.person_category_input = QComboBox()
        for person_category in TrainingPersonCategory:
            self.person_category_input.addItem(
                format_training_person_category_label(person_category),
                person_category.value,
            )
        self.person_category_input.currentIndexChanged.connect(lambda _index: self._sync_scenario_fields())
        form.addRow("Категорія особи", self.person_category_input)

        self.requires_primary_input = QCheckBox("Потребує первинного інструктажу на робочому місці")
        self.requires_primary_input.toggled.connect(lambda _checked: self._sync_scenario_fields())
        form.addRow("", self.requires_primary_input)

        self.event_date_input = DateLineEdit()
        self.event_date_input.setPlaceholderText("ДД.ММ.РРРР")
        self.event_date_input.textChanged.connect(lambda _text: self._sync_scenario_fields())
        form.addRow("Дата проведення", self.event_date_input)

        self.risk_label = self._with_info("Категорія робіт", TRAINING_REPEAT_PERIOD_HINT)
        self.risk_input = QComboBox()
        for risk_category in (
            TrainingWorkRiskCategory.NOT_APPLICABLE,
            TrainingWorkRiskCategory.REGULAR,
            TrainingWorkRiskCategory.HIGH_RISK,
        ):
            self.risk_input.addItem(format_training_work_risk_category_label(risk_category), risk_category.value)
        self.risk_input.currentIndexChanged.connect(lambda _index: self._sync_scenario_fields())
        form.addRow(self.risk_label, self.risk_input)

        self.affects_repeated_input = QCheckBox(
            "Внутрішнім рішенням підприємства перенести дату повторного контролю від дати цього інструктажу"
        )
        self.affects_repeated_input.toggled.connect(lambda _checked: self._sync_scenario_fields())
        form.addRow("", self.affects_repeated_input)

        self.manual_date_input = QCheckBox("Ввести дату наступного контролю вручну")
        self.manual_date_input.toggled.connect(lambda _checked: self._sync_scenario_fields())
        form.addRow("", self.manual_date_input)

        self.next_date_label = QLabel("Наступний контроль")
        self.next_date_input = DateLineEdit()
        self.next_date_input.setPlaceholderText("ДД.ММ.РРРР")
        form.addRow(self.next_date_label, self.next_date_input)

        self.scenario_hint = QLabel()
        self.scenario_hint.setWordWrap(True)
        self.scenario_hint.setStyleSheet(f"color: {COLOR['text_secondary']};")
        form.addRow("", self.scenario_hint)

        self.conducted_by_input = QLineEdit()
        form.addRow("Проводив", self.conducted_by_input)

        self.knowledge_result_input = QComboBox()
        self.knowledge_result_input.addItem("Не відстежувалось раніше", TrainingKnowledgeCheckResult.LEGACY_NOT_TRACKED.value)
        self.knowledge_result_input.addItem("Задовільно", TrainingKnowledgeCheckResult.SATISFACTORY.value)
        self.knowledge_result_input.addItem("Незадовільно", TrainingKnowledgeCheckResult.UNSATISFACTORY.value)
        self.knowledge_result_input.addItem("Не застосовується", TrainingKnowledgeCheckResult.NOT_APPLICABLE.value)
        form.addRow(self._with_info("Результат перевірки\nзнань і навичок", TRAINING_KNOWLEDGE_CHECK_HINT), self.knowledge_result_input)

        self.work_admission_input = QComboBox()
        self.work_admission_input.addItem("Не відстежувалось раніше", TrainingWorkAdmissionStatus.LEGACY_NOT_TRACKED.value)
        self.work_admission_input.addItem("Допущений", TrainingWorkAdmissionStatus.ALLOWED.value)
        self.work_admission_input.addItem("Не допущений", TrainingWorkAdmissionStatus.NOT_ALLOWED.value)
        self.work_admission_input.addItem("Не застосовується", TrainingWorkAdmissionStatus.NOT_APPLICABLE.value)
        form.addRow("Допуск", self.work_admission_input)

        self.knowledge_note_input = QTextEdit()
        self.knowledge_note_input.setMaximumHeight(80)
        form.addRow("Коментар щодо перевірки", self.knowledge_note_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(80)
        form.addRow("Коментар", self.note_input)
        layout.addLayout(form)

        self.basis_panel = BasisNotePanel()
        self.basis_panel.setVisible(False)
        layout.addWidget(self.basis_panel)

        self.feedback_label = FormFeedbackLabel()
        layout.addWidget(self.feedback_label)

        self.save_button = QPushButton("Зберегти запис")
        self.save_button.setProperty("variant", "accent")
        self.save_button.clicked.connect(self._save_record)
        self.delete_button = QPushButton("Видалити запис")
        self.delete_button.setProperty("variant", "secondary")
        self.delete_button.setStyleSheet(f"color: {COLOR['critical']};")
        self.delete_button.clicked.connect(self._delete_record)

        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(SPACING["sm"])
        actions_layout.addWidget(self.save_button, stretch=1)
        actions_layout.addWidget(self.delete_button)
        layout.addLayout(actions_layout)

        self.new_button = QPushButton("Новий запис")
        self.new_button.setProperty("variant", "secondary")
        self.new_button.clicked.connect(self.clear_form)
        layout.addWidget(self.new_button)
        self.clear_form()

    def _with_info(self, text: str, tooltip_text: str) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(QLabel(text))
        row.addWidget(InfoTooltipIcon(tooltip_text))
        row.addStretch()
        return container

    def set_row(self, row: TrainingWorkspaceRow) -> None:
        self._is_updating = True
        self._current_record_id = row.record_id
        self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(row.employee_personnel_number)))
        if row.training_type:
            self.type_input.setCurrentIndex(max(0, self.type_input.findData(row.training_type.value)))
        self.person_category_input.setCurrentIndex(max(0, self.person_category_input.findData(row.person_category.value)))
        self.requires_primary_input.setChecked(row.requires_primary_on_workplace)
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
        self.knowledge_result_input.setCurrentIndex(max(0, self.knowledge_result_input.findData(row.knowledge_check_result.value)))
        self.work_admission_input.setCurrentIndex(max(0, self.work_admission_input.findData(row.work_admission_status.value)))
        self.knowledge_note_input.setPlainText(row.knowledge_check_note)
        self.basis_panel.set_values(row.basis_text, row.basis_note)
        self.save_button.setText("Створити запис" if row.is_missing else "Зберегти зміни")
        self.delete_button.setVisible(not row.is_missing and row.record_id is not None)
        self._is_updating = False
        self._sync_scenario_fields(recalculate=False)

    def clear_form(self) -> None:
        self._is_updating = True
        self._current_record_id = None
        self.type_input.setCurrentIndex(max(0, self.type_input.findData(TrainingType.INTRODUCTORY.value)))
        self.person_category_input.setCurrentIndex(
            max(0, self.person_category_input.findData(TrainingPersonCategory.OWN_EMPLOYEE.value))
        )
        self.requires_primary_input.setChecked(
            build_default_primary_requirement_for_person_category(TrainingPersonCategory.OWN_EMPLOYEE)
        )
        self.event_date_input.clear()
        self.next_date_input.clear()
        self.risk_input.setCurrentIndex(max(0, self.risk_input.findData(TrainingWorkRiskCategory.NOT_APPLICABLE.value)))
        self.affects_repeated_input.setChecked(False)
        self.manual_date_input.setChecked(False)
        self.conducted_by_input.clear()
        self.note_input.clear()
        self.knowledge_result_input.setCurrentIndex(0)
        self.work_admission_input.setCurrentIndex(0)
        self.knowledge_note_input.clear()
        self.basis_panel.clear()
        self.save_button.setText("Створити запис")
        self.delete_button.setVisible(False)
        self._is_updating = False
        self._sync_scenario_fields()

    def current_selection_context(self) -> tuple[int | None, str | None]:
        if self._current_record_id is None:
            return None, None
        personnel_number = self.employee_input.currentData()
        return self._current_record_id, str(personnel_number) if personnel_number is not None else None

    def _sync_scenario_fields(self, recalculate: bool = True) -> None:
        if self._is_updating:
            return

        training_type = TrainingType(str(self.type_input.currentData()))
        person_category = TrainingPersonCategory(str(self.person_category_input.currentData()))
        is_repeated_base = training_type in {TrainingType.PRIMARY, TrainingType.REPEATED}
        is_optional_transfer = training_type in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}
        should_transfer = is_repeated_base or (is_optional_transfer and self.affects_repeated_input.isChecked())

        if person_category == TrainingPersonCategory.VISITOR:
            self.requires_primary_input.setChecked(False)
            self.requires_primary_input.setEnabled(False)
        else:
            self.requires_primary_input.setEnabled(True)

        self.affects_repeated_input.setVisible(is_optional_transfer)
        self.manual_date_input.setVisible(training_type == TrainingType.INTRODUCTORY or should_transfer)
        self.risk_label.setVisible(should_transfer)
        self.risk_input.setVisible(should_transfer)
        self.risk_input.setEnabled(should_transfer)
        self._set_risk_option_enabled(TrainingWorkRiskCategory.NOT_APPLICABLE.value, not should_transfer)
        self.next_date_label.setText(
            "Первинний потрібен до"
            if training_type == TrainingType.INTRODUCTORY and self.requires_primary_input.isChecked()
            else "Наступний контроль"
        )

        if should_transfer and self.risk_input.currentData() == TrainingWorkRiskCategory.NOT_APPLICABLE.value:
            self.risk_input.setCurrentIndex(max(0, self.risk_input.findData(TrainingWorkRiskCategory.REGULAR.value)))
            return
        if not should_transfer:
            self.risk_input.setCurrentIndex(max(0, self.risk_input.findData(TrainingWorkRiskCategory.NOT_APPLICABLE.value)))

        if training_type == TrainingType.INTRODUCTORY:
            self.manual_date_input.setVisible(False)
            self.next_date_input.setReadOnly(True)
        else:
            self.next_date_input.setReadOnly(not self.manual_date_input.isVisible() or not self.manual_date_input.isChecked())

        self.scenario_hint.setText(self._build_scenario_hint(training_type, person_category))
        if not recalculate:
            return

        if training_type == TrainingType.INTRODUCTORY:
            self.next_date_input.setText(self.event_date_input.text().strip() if self.requires_primary_input.isChecked() else "")
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
                person_category,
                self.requires_primary_input.isChecked(),
                TrainingWorkRiskCategory(str(self.risk_input.currentData())),
                None,
                self.affects_repeated_input.isChecked(),
                False,
            )
        except ValueError:
            self.next_date_input.clear()
            return
        self.next_date_input.setText(format_ui_date(next_control_date))

    def _build_scenario_hint(self, training_type: TrainingType, person_category: TrainingPersonCategory) -> str:
        if training_type == TrainingType.INTRODUCTORY:
            if self.requires_primary_input.isChecked():
                return "Після вступного інструктажу первинний інструктаж потрібен до допуску до самостійної роботи."
            if person_category == TrainingPersonCategory.CONTRACTOR:
                return "Вступний інструктаж зафіксовано. Первинний у системі підприємства не потрібен."
            return "Вступний інструктаж зафіксовано без вимоги первинного у системі підприємства."
        if training_type in {TrainingType.UNSCHEDULED, TrainingType.TARGETED} and self.affects_repeated_input.isChecked():
            return "Повторний контроль буде перенесено лише як внутрішнє рішення підприємства."
        if training_type in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}:
            return "Цей запис не змінює план повторного контролю за замовчуванням."
        return "Наступний повторний контроль розраховується автоматично за категорією робіт."

    def _set_risk_option_enabled(self, option_value: str, enabled: bool) -> None:
        index = self.risk_input.findData(option_value)
        if index < 0:
            return
        model = self.risk_input.model()
        if hasattr(model, "item"):
            item = model.item(index)
            if item is not None:
                item.setEnabled(enabled)

    def _save_record(self) -> None:
        training_type = TrainingType(str(self.type_input.currentData()))
        person_category = str(self.person_category_input.currentData())
        requires_primary_on_workplace = self.requires_primary_input.isChecked()
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
        basis_text, basis_note = self.basis_panel.values()

        try:
            if self._current_record_id is None:
                self._current_record_id = create_training_record(
                    self._database_path,
                    str(self.employee_input.currentData()),
                    training_type.value,
                    self.event_date_input.text(),
                    self.next_date_input.text(),
                    self.conducted_by_input.text(),
                    self.note_input.toPlainText(),
                    person_category,
                    requires_primary_on_workplace,
                    work_risk_category,
                    should_update_repeated_control,
                    use_manual_next_control_date,
                    str(self.knowledge_result_input.currentData()),
                    str(self.work_admission_input.currentData()),
                    self.knowledge_note_input.toPlainText(),
                    basis_text,
                    basis_note,
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
                    person_category,
                    requires_primary_on_workplace,
                    work_risk_category,
                    should_update_repeated_control,
                    use_manual_next_control_date,
                    str(self.knowledge_result_input.currentData()),
                    str(self.work_admission_input.currentData()),
                    self.knowledge_note_input.toPlainText(),
                    basis_text,
                    basis_note,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        except Exception as error:  # noqa: BLE001
            self.feedback_label.show_error(f"Не вдалося зберегти запис інструктажу: {error}")
            return

        self.feedback_label.show_success("Запис інструктажу збережено.")
        self.delete_button.setVisible(True)
        self.saved.emit()

    def _delete_record(self) -> None:
        if self._current_record_id is None:
            self.feedback_label.show_error("Для видалення потрібно відкрити існуючий запис.")
            return
        if not self._confirm_delete():
            return

        try:
            delete_training_record(self._database_path, self._current_record_id)
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        except Exception as error:  # noqa: BLE001
            self.feedback_label.show_error(f"Не вдалося видалити запис інструктажу: {error}")
            return

        self.feedback_label.show_success("Запис інструктажу видалено.")
        self.deleted.emit()

    def _confirm_delete(self) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle("Підтвердження")
        box.setText("Ви впевнені, що хочете видалити цей запис інструктажу?")

        yes_button = box.addButton("Видалити", QMessageBox.ButtonRole.AcceptRole)
        yes_button.setStyleSheet(
            "color: #d32f2f; font-weight: bold; padding: 6px 16px; border: 1px solid #ffcdd2; "
            "background: #fff0f0; border-radius: 4px;"
        )
        no_button = box.addButton("Скасувати", QMessageBox.ButtonRole.RejectRole)
        no_button.setStyleSheet(
            "padding: 6px 16px; font-weight: bold; background: #f1f3f5; border: 1px solid #dee2e6; "
            "border-radius: 4px; color: #495057;"
        )
        box.setDefaultButton(no_button)
        box.setStyleSheet(
            f"QMessageBox {{ background: {COLOR['bg_card']}; }} "
            "QLabel { font-size: 14px; margin-bottom: 10px; }"
        )
        box.exec()
        return box.clickedButton() == yes_button
