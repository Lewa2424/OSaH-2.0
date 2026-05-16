from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.employee import Employee
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label
from osah.domain.services.validate_work_permit_participant_change import validate_work_permit_participant_change
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class ChangeWorkPermitParticipantsDialog(QDialog):
    """Модальне вікно керування складом бригади наряду-допуску.
    Modal dialog for editing the work-permit brigade composition.
    """

    def __init__(
        self,
        employees: tuple[Employee, ...],
        participants: tuple[WorkPermitParticipant, ...],
        enforce_change_rules: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._employees = employees
        self._initial_participants = participants
        self._enforce_change_rules = enforce_change_rules
        self._employee_by_number = {
            employee.personnel_number.strip(): employee
            for employee in employees
        }
        self._rows: list[_ParticipantRow] = []

        self.setWindowTitle("Склад бригади")
        self.setModal(True)
        self.resize(680, 420)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel(
            "Змініть склад бригади окремою процедурою. "
            "Якщо вибуває більше 50% учасників, потрібен новий наряд-допуск."
        )
        title.setWordWrap(True)
        layout.addWidget(title)

        self._rows_container = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(SPACING["sm"])
        layout.addWidget(self._rows_container)

        add_button = QPushButton("Додати учасника")
        add_button.setProperty("variant", "secondary")
        add_button.clicked.connect(self._add_empty_row)
        layout.addWidget(add_button)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Скасувати")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        save_button = QPushButton("Застосувати")
        save_button.setProperty("variant", "accent")
        save_button.clicked.connect(self._accept_if_valid)
        buttons_row.addWidget(save_button)
        layout.addLayout(buttons_row)

        seed_participants = participants or self._default_participants()
        for participant in seed_participants:
            self._append_row(
                participant.employee_personnel_number,
                participant.participant_role,
            )
        if not self._rows:
            self._add_empty_row()

    def participants(self) -> tuple[WorkPermitParticipant, ...]:
        """Повертає склад бригади, обраний у діалозі.
        Returns the brigade composition selected in the dialog.
        """

        result: list[WorkPermitParticipant] = []
        for row in self._rows:
            personnel_number = row.personnel_number().strip()
            employee = self._employee_by_number[personnel_number]
            result.append(
                WorkPermitParticipant(
                    employee_personnel_number=personnel_number,
                    employee_full_name=employee.full_name,
                    participant_role=row.role(),
                )
            )
        return tuple(result)

    def _default_participants(self) -> tuple[WorkPermitParticipant, ...]:
        if not self._employees:
            return ()
        first_employee = self._employees[0]
        return (
            WorkPermitParticipant(
                employee_personnel_number=first_employee.personnel_number,
                employee_full_name=first_employee.full_name,
                participant_role=WorkPermitParticipantRole.EXECUTOR,
            ),
        )

    def _add_empty_row(self) -> None:
        self._append_row("", WorkPermitParticipantRole.TEAM_MEMBER)

    def _append_row(self, personnel_number: str, participant_role: WorkPermitParticipantRole) -> None:
        row = _ParticipantRow(self._employees, personnel_number, participant_role)
        row.remove_requested.connect(lambda: self._remove_row(row))
        self._rows.append(row)
        self._rows_layout.addWidget(row)

    def _remove_row(self, row: "_ParticipantRow") -> None:
        if len(self._rows) <= 1:
            self._feedback_label.show_error("У складі бригади має залишатися щонайменше один учасник.")
            return
        self._rows.remove(row)
        self._rows_layout.removeWidget(row)
        row.deleteLater()

    def _accept_if_valid(self) -> None:
        selected_numbers = [row.personnel_number().strip() for row in self._rows]
        if not selected_numbers:
            self._feedback_label.show_error("Потрібно додати щонайменше одного учасника.")
            return
        if any(not personnel_number for personnel_number in selected_numbers):
            self._feedback_label.show_error("Для кожного рядка потрібно вибрати працівника.")
            return
        if len(set(selected_numbers)) != len(selected_numbers):
            self._feedback_label.show_error("Один і той самий працівник не може бути доданий двічі.")
            return
        if self._enforce_change_rules:
            try:
                validate_work_permit_participant_change(self._initial_participants, self.participants())
            except ValueError as error:
                message = str(error)
                if "50%" in message:
                    message += " Скористайтеся кнопкою 'Перевипустити наряд', якщо змінюється більшість бригади."
                self._feedback_label.show_error(message)
                return
        self.accept()


class _ParticipantRow(QWidget):
    """Рядок редагування одного учасника бригади.
    Single editable brigade participant row.
    """

    remove_requested = Signal()

    def __init__(
        self,
        employees: tuple[Employee, ...],
        personnel_number: str,
        participant_role: WorkPermitParticipantRole,
    ) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])

        self._employee_input = QComboBox()
        self._employee_input.addItem("Оберіть працівника", "")
        for employee in employees:
            self._employee_input.addItem(
                f"{employee.full_name} ({employee.personnel_number})",
                employee.personnel_number,
            )
        self._employee_input.setCurrentIndex(max(0, self._employee_input.findData(personnel_number.strip())))
        layout.addWidget(self._employee_input, stretch=1)

        self._role_input = QComboBox()
        for role in WorkPermitParticipantRole:
            self._role_input.addItem(format_work_permit_participant_role_label(role), role.value)
        self._role_input.setCurrentIndex(max(0, self._role_input.findData(participant_role.value)))
        layout.addWidget(self._role_input)

        remove_button = QPushButton("Вилучити")
        remove_button.setProperty("variant", "secondary")
        remove_button.clicked.connect(self._emit_remove_requested)
        layout.addWidget(remove_button)

    def personnel_number(self) -> str:
        """Повертає вибраний табельний номер.
        Returns the selected personnel number.
        """

        return str(self._employee_input.currentData() or "")

    def role(self) -> WorkPermitParticipantRole:
        """Повертає обрану роль учасника.
        Returns the selected participant role.
        """

        return WorkPermitParticipantRole(str(self._role_input.currentData() or WorkPermitParticipantRole.TEAM_MEMBER.value))

    def _emit_remove_requested(self) -> None:
        self.remove_requested.emit()
