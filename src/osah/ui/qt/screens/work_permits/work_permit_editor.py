from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.cancel_work_permit_record import cancel_work_permit_record
from osah.application.services.close_work_permit_record import close_work_permit_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.update_work_permit_record import update_work_permit_record
from osah.domain.entities.employee import Employee
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import SPACING


class WorkPermitEditor(QWidget):
    """Форма створення, редагування, закриття і скасування наряду.
    Form for creating, editing, closing and canceling a work permit.
    """

    saved = Signal()

    def __init__(self, database_path: Path, employees: tuple[Employee, ...]) -> None:
        super().__init__()
        self._database_path = database_path
        self._current_record_id: int | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])
        form = QFormLayout()

        self.permit_number_input = QLineEdit()
        form.addRow("Номер", self.permit_number_input)
        self.work_kind_input = QLineEdit()
        form.addRow("Вид робіт", self.work_kind_input)
        self.work_location_input = QLineEdit()
        form.addRow("Місце", self.work_location_input)

        self.starts_at_input = QLineEdit()
        self.starts_at_input.setPlaceholderText("ДД.ММ.ГГГГ HH:MM")
        form.addRow("Початок", self.starts_at_input)

        self.ends_at_input = QLineEdit()
        self.ends_at_input.setPlaceholderText("ДД.ММ.ГГГГ HH:MM")
        form.addRow("Завершення", self.ends_at_input)

        self.responsible_input = QLineEdit()
        form.addRow("Відповідальний", self.responsible_input)
        self.issuer_input = QLineEdit()
        form.addRow("Допускаючий", self.issuer_input)

        self.employee_input = QComboBox()
        for employee in employees:
            if employee.employment_status.strip().lower() == "active":
                self.employee_input.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
        form.addRow("Учасник", self.employee_input)

        self.role_input = QComboBox()
        for role in WorkPermitParticipantRole:
            self.role_input.addItem(format_work_permit_participant_role_label(role), role.value)
        form.addRow("Роль", self.role_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(70)
        form.addRow("Примітка", self.note_input)
        layout.addLayout(form)

        self.feedback_label = FormFeedbackLabel()
        layout.addWidget(self.feedback_label)

        self.save_button = QPushButton("Зберегти наряд")
        self.save_button.setProperty("variant", "accent")
        self.save_button.clicked.connect(self._save_record)
        layout.addWidget(self.save_button)

        self.close_button = QPushButton("Закрити наряд")
        self.close_button.setProperty("variant", "secondary")
        self.close_button.clicked.connect(self._close_record)
        layout.addWidget(self.close_button)

        self.cancel_reason_input = QLineEdit()
        self.cancel_reason_input.setPlaceholderText("Причина скасування")
        layout.addWidget(self.cancel_reason_input)

        self.cancel_button = QPushButton("Скасувати наряд")
        self.cancel_button.setProperty("variant", "secondary")
        self.cancel_button.clicked.connect(self._cancel_record)
        layout.addWidget(self.cancel_button)

        self.new_button = QPushButton("Новий наряд")
        self.new_button.setProperty("variant", "secondary")
        self.new_button.clicked.connect(self.clear_form)
        layout.addWidget(self.new_button)

    def set_row(self, row: WorkPermitWorkspaceRow) -> None:
        """Заповнює форму вибраним нарядом-допуском.
        Fills the form with the selected work permit.
        """

        self._current_record_id = row.record_id
        self.permit_number_input.setText(row.permit_number)
        self.work_kind_input.setText(row.work_kind)
        self.work_location_input.setText(row.work_location)
        self.starts_at_input.setText(format_ui_datetime(row.starts_at))
        self.ends_at_input.setText(format_ui_datetime(row.ends_at))
        self.responsible_input.setText(row.responsible_person)
        self.issuer_input.setText(row.issuer_person)
        if row.record.participants:
            participant = row.record.participants[0]
            self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(participant.employee_personnel_number)))
            self.role_input.setCurrentIndex(max(0, self.role_input.findData(participant.participant_role.value)))
        self.note_input.setPlainText(row.record.note_text)
        self.save_button.setText("Зберегти зміни")

    def clear_form(self) -> None:
        """Готує форму до створення нового наряду.
        Prepares the form for creating a new work permit.
        """

        self._current_record_id = None
        for field in (
            self.permit_number_input,
            self.work_kind_input,
            self.work_location_input,
            self.starts_at_input,
            self.ends_at_input,
            self.responsible_input,
            self.issuer_input,
            self.cancel_reason_input,
        ):
            field.clear()
        self.note_input.clear()
        self.save_button.setText("Створити наряд")

    def _save_record(self) -> None:
        """Зберігає наряд через application service.
        Saves a work permit through application service.
        """

        try:
            if self._current_record_id is None:
                create_work_permit_record(self._database_path, *self._form_values())
            else:
                update_work_permit_record(self._database_path, self._current_record_id, *self._form_values())
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Наряд-допуск збережено.")
        self.saved.emit()

    def _close_record(self) -> None:
        """Закриває вибраний наряд через окреме application service.
        Closes the selected work permit through a dedicated application service.
        """

        if self._current_record_id is None:
            self.feedback_label.show_error("Спочатку оберіть наряд.")
            return
        try:
            close_work_permit_record(self._database_path, self._current_record_id)
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Наряд-допуск закрито.")
        self.saved.emit()

    def _cancel_record(self) -> None:
        """Скасовує вибраний наряд із фіксацією причини.
        Cancels the selected work permit with a reason.
        """

        if self._current_record_id is None:
            self.feedback_label.show_error("Спочатку оберіть наряд.")
            return
        try:
            cancel_work_permit_record(self._database_path, self._current_record_id, self.cancel_reason_input.text())
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Наряд-допуск скасовано.")
        self.saved.emit()

    def _form_values(self) -> tuple[str, str, str, str, str, str, str, str, str, str]:
        """Повертає значення форми у порядку application service.
        Returns form values in application service order.
        """

        return (
            self.permit_number_input.text(),
            self.work_kind_input.text(),
            self.work_location_input.text(),
            self.starts_at_input.text(),
            self.ends_at_input.text(),
            self.responsible_input.text(),
            self.issuer_input.text(),
            str(self.employee_input.currentData()),
            str(self.role_input.currentData()),
            self.note_input.toPlainText(),
        )
