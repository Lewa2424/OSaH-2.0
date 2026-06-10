from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QLabel, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.apply_work_permit_participant_change import apply_work_permit_participant_change
from osah.application.services.cancel_work_permit_record import cancel_work_permit_record
from osah.application.services.close_work_permit_record import close_work_permit_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.extend_work_permit_record import extend_work_permit_record
from osah.application.services.load_employee_work_readiness import load_employee_work_readiness
from osah.application.services.record_work_permit_daily_check import record_work_permit_daily_check
from osah.application.services.suggest_followup_work_permit_number import suggest_followup_work_permit_number
from osah.application.services.update_work_permit_record import update_work_permit_record
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_readiness_level import EmployeeReadinessLevel
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.build_work_permit_daily_check_summary import build_work_permit_daily_check_summary
from osah.domain.services.format_ui_date import format_ui_date
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label
from osah.domain.services.format_work_permit_target_training_status_label import format_work_permit_target_training_status_label
from osah.domain.services.list_work_permit_kind_options import list_work_permit_kind_options
from osah.domain.services.normalize_work_permit_target_training_status import normalize_work_permit_target_training_status
from osah.domain.services.normalize_ui_datetime_text import normalize_ui_datetime_text
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text
from osah.ui.qt.components.basis_note_panel import BasisNotePanel
from osah.ui.qt.components.date_line_edit import DateLineEdit
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.info_tooltip_icon import InfoTooltipIcon
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.hints.normative_hints import (
    WORK_PERMIT_KIND_HINT,
    WORK_PERMIT_PARTICIPANT_READINESS_HINT,
    WORK_PERMIT_TARGET_TRAINING_HINT,
)
from osah.ui.qt.screens.work_permits.build_work_permit_extension_summary import build_work_permit_extension_summary
from osah.ui.qt.screens.work_permits.cancel_work_permit_dialog import CancelWorkPermitDialog
from osah.ui.qt.screens.work_permits.change_work_permit_participants_dialog import ChangeWorkPermitParticipantsDialog
from osah.ui.qt.screens.work_permits.close_work_permit_dialog import CloseWorkPermitDialog
from osah.ui.qt.screens.work_permits.extend_work_permit_dialog import ExtendWorkPermitDialog
from osah.ui.qt.screens.work_permits.record_work_permit_daily_check_dialog import RecordWorkPermitDailyCheckDialog


class WorkPermitEditor(QWidget):
    """Форма створення і редагування наряду-допуску.
    Form for creating and editing a work permit.
    """

    saved = Signal()
    module_navigation_requested = Signal(AppSection, str)

    def __init__(self, database_path: Path, employees: tuple[Employee, ...], access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._read_only = access_role != AccessRole.INSPECTOR
        self._current_record_id: int | None = None
        self._current_record: WorkPermitRecord | None = None
        self._active_employees = tuple(
            employee for employee in employees if employee.employment_status.strip().lower() == "active"
        )
        self._participants: tuple[WorkPermitParticipant, ...] = ()
        self._pending_reissue_participants: tuple[WorkPermitParticipant, ...] = ()
        self._work_permit_kind_options = list_work_permit_kind_options()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        self.manage_participants_button = QPushButton("1. Задати склад бригади")
        self.manage_participants_button.setProperty("variant", "secondary")
        self.manage_participants_button.clicked.connect(self._manage_participants)
        layout.addWidget(self.manage_participants_button)

        layout.addWidget(self._section_title("Дані наряду"))
        permit_form = QFormLayout()

        self.permit_number_input = QLineEdit()
        permit_form.addRow("Номер", self.permit_number_input)

        self.work_kind_selector = QComboBox()
        self._populate_work_kind_selector()
        self.work_kind_selector.currentIndexChanged.connect(self._apply_selected_work_kind_option)
        permit_form.addRow("Тип наряду", self.work_kind_selector)

        self.work_kind_input = QLineEdit()
        self.work_kind_input.textChanged.connect(self._handle_work_kind_text_changed)
        self.work_kind_input.setPlaceholderText(
            "Наприклад: вогневі, газонебезпечні, висотні, ремонтні, вантажопідіймальні."
        )
        permit_form.addRow(self._with_info("Вид робіт", WORK_PERMIT_KIND_HINT), self.work_kind_input)

        self._work_kind_guidance_label = QLabel("Оберіть типовий варіант або задайте вид робіт вручну.")
        self._work_kind_guidance_label.setWordWrap(True)
        self._work_kind_guidance_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        permit_form.addRow("", self._work_kind_guidance_label)

        self.work_location_input = QLineEdit()
        permit_form.addRow("Місце", self.work_location_input)

        self.starts_at_input = QLineEdit()
        self.starts_at_input.editingFinished.connect(lambda: self._normalize_datetime_input(self.starts_at_input))
        self.starts_at_input.setPlaceholderText("ДД.ММ.РРРР HH:MM")
        permit_form.addRow("Початок", self.starts_at_input)

        self.ends_at_input = QLineEdit()
        self.ends_at_input.editingFinished.connect(lambda: self._normalize_datetime_input(self.ends_at_input))
        self.ends_at_input.setPlaceholderText("ДД.ММ.РРРР HH:MM")
        permit_form.addRow("Завершення", self.ends_at_input)

        self.responsible_input = QLineEdit()
        permit_form.addRow("Керівник робіт", self.responsible_input)

        self.issuer_input = QLineEdit()
        self.issuer_input.setPlaceholderText("Необов'язково для контрольного реєстру")
        permit_form.addRow("Допускаючий", self.issuer_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(76)
        permit_form.addRow("Примітка", self.note_input)
        layout.addLayout(permit_form)

        layout.addWidget(self._section_title("Строк дії та продовження"))
        self._base_term_label = QLabel()
        self._current_term_label = QLabel()
        self._extension_state_label = QLabel()
        self._extension_reason_label = QLabel()
        self._schedule_notice_label = QLabel()
        self._schedule_notice_label.setWordWrap(True)
        self._schedule_notice_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(self._base_term_label)
        layout.addWidget(self._current_term_label)
        layout.addWidget(self._extension_state_label)
        layout.addWidget(self._extension_reason_label)
        layout.addWidget(self._schedule_notice_label)

        self.extend_button = QPushButton("Продовжити наряд")
        self.extend_button.setProperty("variant", "secondary")
        self.extend_button.clicked.connect(self._extend_record)
        layout.addWidget(self.extend_button)

        self.reissue_button = QPushButton("Перевипустити наряд")
        self.reissue_button.setProperty("variant", "secondary")
        self.reissue_button.setText("Створити новий на основі цього")
        self.reissue_button.clicked.connect(self._reissue_record)
        layout.addWidget(self.reissue_button)

        lifecycle_actions = QHBoxLayout()
        self.close_button = QPushButton("Закрити наряд")
        self.close_button.setProperty("variant", "secondary")
        self.close_button.clicked.connect(self._close_record)
        lifecycle_actions.addWidget(self.close_button)

        self.cancel_button = QPushButton("Скасувати наряд")
        self.cancel_button.setProperty("variant", "secondary")
        self.cancel_button.clicked.connect(self._cancel_record)
        lifecycle_actions.addWidget(self.cancel_button)
        layout.addLayout(lifecycle_actions)

        layout.addWidget(self._section_title("Щоденні перевірки"))
        self._daily_check_requirement_label = QLabel()
        self._daily_check_requirement_label.setWordWrap(True)
        self._daily_check_last_label = QLabel()
        self._daily_check_history_label = QLabel()
        self._daily_check_history_label.setWordWrap(True)
        self._daily_check_history_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(self._daily_check_requirement_label)
        layout.addWidget(self._daily_check_last_label)
        layout.addWidget(self._daily_check_history_label)

        self.record_daily_check_button = QPushButton("Зафіксувати щоденну перевірку")
        self.record_daily_check_button.setProperty("variant", "secondary")
        self.record_daily_check_button.clicked.connect(self._record_daily_check)
        layout.addWidget(self.record_daily_check_button)

        layout.addWidget(self._section_title("2. Цільовий інструктаж (для всієї бригади)"))
        target_hint = QLabel(
            "Один раз заповніть для наряду — запис з'явиться у всіх учасників у розділі «Інструктажі». "
            "Потім натисніть «Зберегти зміни» внизу."
        )
        target_hint.setWordWrap(True)
        target_hint.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(target_hint)
        target_form = QFormLayout()

        self.target_training_status_input = QComboBox()
        for status in (
            WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED,
            WorkPermitTargetTrainingStatus.NOT_DONE,
            WorkPermitTargetTrainingStatus.DONE_PASSED,
            WorkPermitTargetTrainingStatus.DONE_FAILED,
        ):
            self.target_training_status_input.addItem(
                format_work_permit_target_training_status_label(status),
                status.value,
            )
        target_form.addRow(
            self._with_info("Стан цільового інструктажу", WORK_PERMIT_TARGET_TRAINING_HINT),
            self.target_training_status_input,
        )

        self.target_training_date_input = DateLineEdit()
        self.target_training_date_input.setPlaceholderText("ДД.ММ.РРРР")
        target_form.addRow("Дата інструктажу", self.target_training_date_input)

        self.target_training_conducted_by_input = QLineEdit()
        target_form.addRow("Хто провів", self.target_training_conducted_by_input)

        self.target_training_note_input = QTextEdit()
        self.target_training_note_input.setMaximumHeight(64)
        target_form.addRow("Коментар", self.target_training_note_input)
        layout.addLayout(target_form)

        layout.addWidget(self._section_title("Учасники та перевірка стану"))
        participant_form = QFormLayout()

        self.employee_input = QComboBox()
        self.employee_input.currentIndexChanged.connect(self._handle_current_participant_changed)
        participant_form.addRow("Поточний учасник", self.employee_input)

        self.role_input = QComboBox()
        for role in WorkPermitParticipantRole:
            self.role_input.addItem(format_work_permit_participant_role_label(role), role.value)
        participant_form.addRow("Роль", self.role_input)
        layout.addLayout(participant_form)

        self._readiness_title = self._with_info("Стан учасника", WORK_PERMIT_PARTICIPANT_READINESS_HINT)
        self._training_readiness_label = QLabel("Інструктажі: -")
        self._medical_readiness_label = QLabel("Медицина: -")
        self._ppe_readiness_label = QLabel("ЗІЗ: -")
        layout.addWidget(self._readiness_title)
        layout.addWidget(self._training_readiness_label)
        layout.addWidget(self._medical_readiness_label)
        layout.addWidget(self._ppe_readiness_label)

        readiness_actions = QHBoxLayout()
        self._open_training_button = QPushButton("Відкрити інструктажі")
        self._open_training_button.setProperty("variant", "secondary")
        self._open_training_button.clicked.connect(lambda: self._open_module(AppSection.TRAININGS))
        self._open_medical_button = QPushButton("Відкрити медицину")
        self._open_medical_button.setProperty("variant", "secondary")
        self._open_medical_button.clicked.connect(lambda: self._open_module(AppSection.MEDICAL))
        self._open_ppe_button = QPushButton("Відкрити ЗІЗ")
        self._open_ppe_button.setProperty("variant", "secondary")
        self._open_ppe_button.clicked.connect(lambda: self._open_module(AppSection.PPE))
        readiness_actions.addWidget(self._open_training_button)
        readiness_actions.addWidget(self._open_medical_button)
        readiness_actions.addWidget(self._open_ppe_button)
        layout.addLayout(readiness_actions)

        self.basis_panel = BasisNotePanel()
        self.basis_panel.setVisible(False)
        layout.addWidget(self.basis_panel)

        self.feedback_label = FormFeedbackLabel()
        layout.addWidget(self.feedback_label)

        self.save_button = QPushButton("Зберегти зміни")
        self.save_button.setProperty("variant", "accent")
        self.save_button.clicked.connect(self._save_record)
        layout.addWidget(self.save_button)

        self.clear_form()
        self._apply_read_only_mode()

    def current_employee_personnel_number(self) -> str:
        """Повертає табельний номер поточного учасника.
        Returns the current participant personnel number.
        """

        return str(self.employee_input.currentData() or "").strip()

    def current_record_id(self) -> int | None:
        """Повертає id поточного відкритого наряду.
        Returns the current open work-permit id.
        """

        return self._current_record_id

    def set_row(self, row: WorkPermitWorkspaceRow) -> None:
        """Заповнює форму значеннями вибраного наряду.
        Populates the form with the selected permit values.
        """

        self._current_record_id = row.record_id
        self._current_record = row.record
        self._participants = row.record.participants
        self._pending_reissue_participants = ()
        self._set_participant_options(self._participants, row.employee_numbers[0] if row.employee_numbers else None)
        self._apply_participants_mode()
        self._apply_reissue_mode()
        self._apply_lifecycle_actions_mode()

        self.permit_number_input.setText(row.permit_number)
        self.work_kind_input.setText(row.work_kind)
        self._sync_work_kind_selector(row.work_kind)
        self.work_location_input.setText(row.work_location)
        self.starts_at_input.setText(format_ui_datetime(row.starts_at))
        self.ends_at_input.setText(format_ui_datetime(row.ends_at))
        self.responsible_input.setText(row.responsible_person)
        self.issuer_input.setText(row.issuer_person)
        self.note_input.setPlainText(row.record.note_text)

        normalized_status = normalize_work_permit_target_training_status(row.record.target_training_status)
        self.target_training_status_input.setCurrentIndex(
            max(0, self.target_training_status_input.findData(normalized_status.value))
        )
        self.target_training_date_input.setText(format_ui_date(row.record.target_training_date))
        self.target_training_conducted_by_input.setText(row.record.target_training_conducted_by)
        self.target_training_note_input.setPlainText(row.record.target_training_note)
        self.basis_panel.set_values(row.record.basis_text, row.record.basis_note)
        self.save_button.setText("Зберегти зміни")
        self._sync_role_for_current_participant()
        self._refresh_readiness_panel()
        self._apply_extension_summary()
        self._apply_daily_check_summary()
        self._apply_read_only_mode()

    def clear_form(self) -> None:
        """Очищує форму та переводить редактор у режим нового наряду.
        Clears the form and switches the editor to new permit mode.
        """

        self._current_record_id = None
        self._current_record = None
        self._participants = ()
        self._pending_reissue_participants = ()
        for field in (
            self.permit_number_input,
            self.work_kind_input,
            self.work_location_input,
            self.starts_at_input,
            self.ends_at_input,
            self.responsible_input,
            self.issuer_input,
            self.target_training_date_input,
            self.target_training_conducted_by_input,
        ):
            field.clear()
        self.note_input.clear()
        self.target_training_note_input.clear()
        self.basis_panel.clear()
        self.target_training_status_input.setCurrentIndex(0)
        self.work_kind_selector.setCurrentIndex(0)
        self._sync_work_kind_selector("")
        self._set_participant_options(None, None)
        self._apply_participants_mode()
        self._apply_reissue_mode()
        self._apply_lifecycle_actions_mode()
        self.save_button.setText("Створити наряд")
        self._refresh_readiness_panel()
        self._apply_extension_summary()
        self._apply_daily_check_summary()
        self._apply_read_only_mode()

    def _section_title(self, text: str) -> QLabel:
        """Створює простий внутрішній заголовок блоку форми.
        Creates a simple internal section heading for the form.
        """

        title = QLabel(text)
        title.setStyleSheet("font-size: 14px; font-weight: 900;")
        return title

    def _normalize_datetime_input(self, field: QLineEdit) -> None:
        """Normalizes flexible datetime input to canonical UI format."""

        normalized_text = field.text().strip()
        if not normalized_text or field.isReadOnly():
            return
        try:
            field.setText(normalize_ui_datetime_text(normalized_text))
            self.feedback_label.clear()
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            field.setFocus()
            field.selectAll()

    def _populate_work_kind_selector(self) -> None:
        """Наповнює список типових видів нарядів без жорсткої галузевої валідації.
        Populates the list of typical permit kinds without strict sector-specific validation.
        """

        self.work_kind_selector.addItem("Оберіть типовий варіант", "")
        for option in self._work_permit_kind_options:
            self.work_kind_selector.addItem(option.label, option.key)

    def _apply_selected_work_kind_option(self) -> None:
        """Підставляє вибраний типовий вид наряду та коротку підказку в форму.
        Applies the selected typical permit kind and a short guidance note to the form.
        """

        option_key = str(self.work_kind_selector.currentData() or "").strip()
        if not option_key:
            self._work_kind_guidance_label.setText("Оберіть типовий варіант або задайте вид робіт вручну.")
            return

        for option in self._work_permit_kind_options:
            if option.key != option_key:
                continue
            if option.key != "other":
                self.work_kind_input.setText(option.label)
            self._work_kind_guidance_label.setText(option.guidance_text)
            return

    def _handle_work_kind_text_changed(self, value: str) -> None:
        """Синхронізує ручний текст виду робіт із типовим списком, якщо знайдено збіг.
        Synchronizes the manual work-kind text with the typical list when a match exists.
        """

        self._sync_work_kind_selector(value)

    def _sync_work_kind_selector(self, work_kind_text: str) -> None:
        """Вирівнює випадаючий список із поточним текстом виду робіт.
        Aligns the dropdown with the current work-kind text.
        """

        normalized_text = work_kind_text.strip().lower()
        matched_index = 0
        guidance_text = "Оберіть типовий варіант або задайте вид робіт вручну."
        if normalized_text:
            other_index = self.work_kind_selector.findData("other")
            matched_index = other_index if other_index >= 0 else 0
            guidance_text = "Користувацький вид робіт. Система збереже його як універсальний наряд без окремої галузевої валідації."
        for option in self._work_permit_kind_options:
            if option.label.strip().lower() != normalized_text:
                continue
            found_index = self.work_kind_selector.findData(option.key)
            matched_index = found_index if found_index >= 0 else matched_index
            guidance_text = option.guidance_text
            break

        self.work_kind_selector.blockSignals(True)
        self.work_kind_selector.setCurrentIndex(matched_index)
        self.work_kind_selector.blockSignals(False)
        self._work_kind_guidance_label.setText(guidance_text)

    def _with_info(self, text: str, tooltip_text: str) -> QWidget:
        """Повертає підпис поля з нормативною підказкою.
        Returns a field label with a normative tooltip.
        """

        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(QLabel(text))
        row.addWidget(InfoTooltipIcon(tooltip_text))
        row.addStretch()
        return container

    def _set_participant_options(
        self,
        participants: tuple[WorkPermitParticipant, ...] | None,
        selected_personnel_number: str | None,
    ) -> None:
        """Налаштовує список поточних учасників для редагування або створення.
        Configures current participant choices for editing or creation.
        """

        self.employee_input.blockSignals(True)
        self.employee_input.clear()
        self.employee_input.addItem("Не вибрано", "")
        if participants:
            for participant in participants:
                self.employee_input.addItem(
                    f"{participant.employee_full_name} ({participant.employee_personnel_number})",
                    participant.employee_personnel_number,
                )
            target_personnel_number = selected_personnel_number or participants[0].employee_personnel_number
        else:
            for employee in self._active_employees:
                self.employee_input.addItem(f"{employee.full_name} ({employee.personnel_number})", employee.personnel_number)
            target_personnel_number = selected_personnel_number or ""

        if target_personnel_number:
            self.employee_input.setCurrentIndex(max(0, self.employee_input.findData(target_personnel_number)))
        elif self.employee_input.count():
            self.employee_input.setCurrentIndex(0)
        self.employee_input.blockSignals(False)
        self._sync_role_for_current_participant()

    def _apply_participants_mode(self) -> None:
        """Оновлює підпис кнопки окремого керування складом бригади.
        Refreshes the separate brigade-management button label.
        """

        if self._current_record_id is None:
            self.manage_participants_button.setText("1. Задати склад бригади")
            return
        self.manage_participants_button.setText("1. Змінити склад бригади")

    def _apply_reissue_mode(self) -> None:
        """Оновлює доступність окремої дії перевипуску наряду.
        Refreshes availability of the separate permit-reissue action.
        """

        if self._read_only:
            self.feedback_label.show_error("Режим read-only: продовження недоступне.")
            return
        if self._current_record is None or self._current_record.record_id is None:
            self.reissue_button.setEnabled(False)
            return
        self.reissue_button.setEnabled(
            self._current_record.status in {WorkPermitStatus.EXPIRED, WorkPermitStatus.CLOSED, WorkPermitStatus.CANCELED}
        )

    def _apply_lifecycle_actions_mode(self) -> None:
        """Оновлює доступність явних дій життєвого циклу наряду.
        Refreshes availability of explicit permit lifecycle actions.
        """

        is_editable_record = (
            self._current_record is not None
            and self._current_record.record_id is not None
            and not self._current_record.closed_at
            and not self._current_record.canceled_at
        )
        self.close_button.setEnabled(is_editable_record)
        self.cancel_button.setEnabled(is_editable_record)

    def _start_new_record_from_current(self) -> None:
        """Р“РѕС‚СѓС” РЅРѕРІРёР№ С‡РµСЂРЅРѕРІРёРє РЅР° РѕСЃРЅРѕРІС– РїРѕС‚РѕС‡РЅРѕРіРѕ РЅР°СЂСЏРґСѓ.
        Prepares a new draft based on the current permit.
        """

        if self._current_record is None:
            raise ValueError("Поточний наряд не вибрано.")

        source_permit_number = self.permit_number_input.text().strip()
        suggested_number = suggest_followup_work_permit_number(self._database_path, source_permit_number)
        participants = self._pending_reissue_participants or self._effective_participants()
        work_kind = self.work_kind_input.text()
        work_location = self.work_location_input.text()
        responsible_person = self.responsible_input.text()
        issuer_person = self.issuer_input.text()
        note_text = self.note_input.toPlainText()
        target_training_status = str(
            self.target_training_status_input.currentData() or WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED.value
        )
        target_training_date = self.target_training_date_input.text()
        target_training_conducted_by = self.target_training_conducted_by_input.text()
        target_training_note = self.target_training_note_input.toPlainText()
        basis_text, basis_note = self.basis_panel.values()

        self.clear_form()
        self._participants = participants
        selected_personnel_number = participants[0].employee_personnel_number if participants else None
        self._set_participant_options(participants, selected_personnel_number)
        self._refresh_readiness_panel()
        self.permit_number_input.setText(suggested_number)
        self.work_kind_input.setText(work_kind)
        self._sync_work_kind_selector(work_kind)
        self.work_location_input.setText(work_location)
        self.responsible_input.setText(responsible_person)
        self.issuer_input.setText(issuer_person)
        self.note_input.setPlainText(note_text)
        self.target_training_status_input.setCurrentIndex(max(0, self.target_training_status_input.findData(target_training_status)))
        self.target_training_date_input.setText(target_training_date)
        self.target_training_conducted_by_input.setText(target_training_conducted_by)
        self.target_training_note_input.setPlainText(target_training_note)
        self.basis_panel.set_values(basis_text, basis_note)
        self.feedback_label.show_success(
            "Підготовлено новий чернетковий наряд на основі поточного. Вкажіть нові строки та перевірте цільовий інструктаж перед збереженням."
        )

    def _seed_participants_for_management(self) -> tuple[WorkPermitParticipant, ...]:
        """Повертає стартовий склад для окремого діалогу бригади.
        Returns the initial participant set for the dedicated brigade dialog.
        """

        participants = self._effective_participants()
        if participants:
            return participants

        personnel_number = self.current_employee_personnel_number()
        if not personnel_number:
            return ()

        current_text = self.employee_input.currentText().strip()
        full_name = current_text.rsplit("(", 1)[0].strip() if "(" in current_text else current_text
        return (
            WorkPermitParticipant(
                employee_personnel_number=personnel_number,
                employee_full_name=full_name,
                participant_role=WorkPermitParticipantRole(
                    str(self.role_input.currentData() or WorkPermitParticipantRole.EXECUTOR.value)
                ),
            ),
        )

    def _handle_current_participant_changed(self) -> None:
        """Синхронізує роль і стан після зміни поточного учасника.
        Synchronizes role and readiness after current participant change.
        """

        self._sync_role_for_current_participant()
        self._refresh_readiness_panel()

    def _sync_role_for_current_participant(self) -> None:
        """Підтягує роль вибраного учасника у форму.
        Loads the selected participant role into the form.
        """

        personnel_number = self.current_employee_personnel_number()
        if not personnel_number or not self._participants:
            return
        for participant in self._participants:
            if participant.employee_personnel_number == personnel_number:
                self.role_input.setCurrentIndex(max(0, self.role_input.findData(participant.participant_role.value)))
                return

    def _effective_participants(self) -> tuple[WorkPermitParticipant, ...]:
        """Формує склад учасників, який потрібно зберегти.
        Builds the participant set that should be saved.
        """

        current_number = self.current_employee_personnel_number()
        current_role = WorkPermitParticipantRole(str(self.role_input.currentData() or WorkPermitParticipantRole.EXECUTOR.value))
        current_text = self.employee_input.currentText().strip()
        if self._participants:
            updated: list[WorkPermitParticipant] = []
            for participant in self._participants:
                if participant.employee_personnel_number == current_number:
                    updated.append(
                        WorkPermitParticipant(
                            employee_personnel_number=participant.employee_personnel_number,
                            employee_full_name=participant.employee_full_name,
                            participant_role=current_role,
                        )
                    )
                else:
                    updated.append(participant)
            return tuple(updated)

        if not current_number:
            return ()
        full_name = current_text.rsplit("(", 1)[0].strip() if "(" in current_text else current_text
        return (
            WorkPermitParticipant(
                employee_personnel_number=current_number,
                employee_full_name=full_name,
                participant_role=current_role,
            ),
        )

    def _refresh_readiness_panel(self) -> None:
        """Оновлює текстову панель стану для поточного учасника.
        Refreshes the textual readiness panel for the current participant.
        """

        personnel_number = self.current_employee_personnel_number()
        if not personnel_number:
            self._training_readiness_label.setText("Інструктажі: немає даних")
            self._medical_readiness_label.setText("Медицина: немає даних")
            self._ppe_readiness_label.setText("ЗІЗ: немає даних")
            return
        readiness = load_employee_work_readiness(self._database_path, personnel_number)
        self._training_readiness_label.setText(
            f"Інструктажі: {self._readiness_text(readiness.training_level)}. {readiness.training_message}"
        )
        self._medical_readiness_label.setText(
            f"Медицина: {self._readiness_text(readiness.medical_level)}. {readiness.medical_message}"
        )
        self._ppe_readiness_label.setText(f"ЗІЗ: {self._readiness_text(readiness.ppe_level)}. {readiness.ppe_message}")

    def _readiness_text(self, level: EmployeeReadinessLevel) -> str:
        """Повертає короткий текст рівня готовності для UI.
        Returns a short readiness level text for the UI.
        """

        mapping = {
            EmployeeReadinessLevel.NORMAL: "Норма",
            EmployeeReadinessLevel.WARNING: "Увага",
            EmployeeReadinessLevel.CRITICAL: "Критично",
            EmployeeReadinessLevel.UNKNOWN: "Немає даних",
        }
        return mapping[level]

    def _open_module(self, section: AppSection) -> None:
        """Відкриває пов'язаний модуль для поточного учасника.
        Opens a related module for the current participant.
        """

        personnel_number = self.current_employee_personnel_number()
        if personnel_number:
            self.module_navigation_requested.emit(section, personnel_number)

    def _manage_participants(self) -> None:
        """Запускає окремий сценарій зміни складу бригади.
        Opens the dedicated brigade-composition workflow.
        """

        if self._read_only:
            self.feedback_label.show_error("Режим read-only: зміна складу бригади недоступна.")
            return

        dialog = ChangeWorkPermitParticipantsDialog(
            self._active_employees,
            self._seed_participants_for_management(),
            enforce_change_rules=False,
            parent=self,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        participants = dialog.participants()
        if self._current_record_id is None:
            self._participants = participants
            selected_personnel_number = participants[0].employee_personnel_number if participants else None
            self._set_participant_options(participants, selected_personnel_number)
            self._refresh_readiness_panel()
            self.feedback_label.show_success("Склад бригади підготовлено для нового наряду.")
            return

        try:
            outcome = apply_work_permit_participant_change(
                self._database_path,
                int(self._current_record_id),
                participants,
                access_role=self._access_role,
            )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            if False:
                message = ""
                message += " Новий склад підготовлено для кнопки 'Перевипустити наряд'."
            return

        self._current_record_id = int(outcome.applied_record_id)
        self._participants = participants
        self._pending_reissue_participants = ()
        selected_personnel_number = participants[0].employee_personnel_number if participants else None
        self._set_participant_options(participants, selected_personnel_number)
        self._refresh_readiness_panel()
        if outcome.reissued:
            self.feedback_label.show_success(
                "Склад бригади змінено. Через заміну понад 50% автоматично створено новий наряд."
            )
            self.saved.emit()
            return
        self.feedback_label.show_success("Склад бригади оновлено.")
        self.saved.emit()

    def _apply_read_only_mode(self) -> None:
        """Disables mutating permit controls for read-only roles."""

        for widget in (
            self.manage_participants_button,
            self.permit_number_input,
            self.work_kind_selector,
            self.work_kind_input,
            self.work_location_input,
            self.starts_at_input,
            self.ends_at_input,
            self.responsible_input,
            self.issuer_input,
            self.note_input,
            self.target_training_status_input,
            self.target_training_date_input,
            self.target_training_conducted_by_input,
            self.target_training_note_input,
            self.employee_input,
            self.role_input,
        ):
            widget.setEnabled(not self._read_only)
        for button in (
            self.extend_button,
            self.reissue_button,
            self.close_button,
            self.cancel_button,
            self.record_daily_check_button,
            self.save_button,
        ):
            button.setVisible(not self._read_only)
            button.setEnabled(not self._read_only)

    def _apply_extension_summary(self) -> None:
        """Оновлює блок строку дії та режим редагування дат.
        Refreshes the term/extension block and the date-edit mode.
        """

        summary = build_work_permit_extension_summary(self._current_record)
        self._base_term_label.setText(str(summary["base_term_text"]))
        self._current_term_label.setText(str(summary["current_term_text"]))
        self._extension_state_label.setText(str(summary["state_text"]))
        self._extension_reason_label.setText(str(summary["reason_text"]))
        self._schedule_notice_label.setText(str(summary["notice_text"]))
        self.extend_button.setEnabled(bool(summary["can_extend"]))
        self.starts_at_input.setReadOnly(bool(summary["lock_dates"]))
        self.ends_at_input.setReadOnly(bool(summary["lock_dates"]))

    def _apply_daily_check_summary(self) -> None:
        """Оновлює блок щоденних перевірок для поточного наряду.
        Refreshes the daily-check block for the current permit.
        """

        summary = build_work_permit_daily_check_summary(self._current_record)
        self._daily_check_requirement_label.setText(str(summary["requirement_text"]))
        self._daily_check_last_label.setText(str(summary["last_check_text"]))
        self._daily_check_history_label.setText(str(summary["history_text"]))
        self.record_daily_check_button.setEnabled(bool(summary["can_record"]))

    def _build_reissued_record(self) -> WorkPermitRecord:
        """Готує новий наряд для операції перевипуску з поточних полів форми.
        Builds the new permit payload for a reissue operation from current form fields.
        """

        starts_at = parse_ui_datetime_text(self.starts_at_input.text())
        ends_at = parse_ui_datetime_text(self.ends_at_input.text())
        permit_number = self.permit_number_input.text().strip()
        work_kind = self.work_kind_input.text().strip()
        work_location = self.work_location_input.text().strip()
        responsible_person = self.responsible_input.text().strip()
        issuer_person = self.issuer_input.text().strip()
        participants = self._pending_reissue_participants or self._effective_participants()
        if not permit_number or not work_kind or not work_location:
            raise ValueError("Номер наряду, вид робіт і місце робіт обов'язкові.")
        if not responsible_person:
            raise ValueError("Потрібно вказати керівника робіт.")
        target_training_date = ""
        if self.target_training_date_input.text().strip():
            target_training_date = parse_ui_date_text(self.target_training_date_input.text().strip()).isoformat()
        target_training_status = WorkPermitTargetTrainingStatus(
            str(self.target_training_status_input.currentData() or WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED.value)
        )
        target_training_conducted_by = self.target_training_conducted_by_input.text().strip()
        if target_training_status in {
            WorkPermitTargetTrainingStatus.DONE_PASSED,
            WorkPermitTargetTrainingStatus.DONE_FAILED,
            WorkPermitTargetTrainingStatus.DONE,
        } and (not target_training_date or not target_training_conducted_by):
            raise ValueError("Для проведеного цільового інструктажу потрібно вказати дату та особу, яка його провела.")

        basis_text, basis_note = self.basis_panel.values()
        return WorkPermitRecord(
            record_id=None,
            permit_number=permit_number,
            work_kind=work_kind,
            work_location=work_location,
            starts_at=starts_at.isoformat(sep=" ", timespec="minutes"),
            ends_at=ends_at.isoformat(sep=" ", timespec="minutes"),
            responsible_person=responsible_person,
            issuer_person=issuer_person,
            note_text=self.note_input.toPlainText().strip(),
            closed_at=None,
            participants=participants,
            status=WorkPermitStatus.ACTIVE,
            base_ends_at=ends_at.isoformat(sep=" ", timespec="minutes"),
            target_training_status=target_training_status,
            target_training_date=target_training_date,
            target_training_conducted_by=target_training_conducted_by,
            target_training_note=self.target_training_note_input.toPlainText().strip(),
            basis_text=basis_text,
            basis_note=basis_note,
        )

    def _extend_record(self) -> None:
        """Відкриває діалог і виконує одноразове продовження строку наряду.
        Opens the dialog and performs one-time permit extension.
        """

        if self._current_record is None or self._current_record.record_id is None:
            self.feedback_label.show_error("Продовження доступне лише для збереженого наряду.")
            return

        summary = build_work_permit_extension_summary(self._current_record)
        if not bool(summary["can_extend"]):
            self.feedback_label.show_error(str(summary["state_text"]))
            return

        dialog = ExtendWorkPermitDialog(format_ui_datetime(self._current_record.ends_at), self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        try:
            extend_work_permit_record(
                self._database_path,
                int(self._current_record.record_id),
                dialog.extended_until_text(),
                dialog.extension_reason_text(),
                access_role=self._access_role,
            )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return

        target_training_status = WorkPermitTargetTrainingStatus(
            str(self.target_training_status_input.currentData() or WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED.value)
        )
        if target_training_status in {
            WorkPermitTargetTrainingStatus.NOT_DONE,
            WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED,
        }:
            self.feedback_label.show_success(
                "Наряд продовжено. Перевірте, чи потрібен повторний допуск і цільовий/позачерговий інструктаж. У реєстрі цільовий інструктаж зараз не зафіксовано."
            )
        else:
            self.feedback_label.show_success(
                "Наряд продовжено. Перевірте, чи потрібен повторний допуск і цільовий/позачерговий інструктаж за вашими правилами."
            )
        self.saved.emit()

    def _record_daily_check(self) -> None:
        """Фіксує щоденну перевірку місця виконання робіт через окремий діалог.
        Records a daily work-area check through a dedicated dialog.
        """

        if self._read_only:
            self.feedback_label.show_error("Режим read-only: щоденна перевірка недоступна.")
            return
        if self._current_record is None or self._current_record.record_id is None:
            self.feedback_label.show_error("Щоденна перевірка доступна лише для збереженого наряду.")
            return

        summary = build_work_permit_daily_check_summary(self._current_record)
        if not bool(summary["can_record"]):
            self.feedback_label.show_error(str(summary["requirement_text"]))
            return

        dialog = RecordWorkPermitDailyCheckDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        try:
            record_work_permit_daily_check(
                self._database_path,
                int(self._current_record.record_id),
                dialog.checked_at_text(),
                dialog.checked_by_text(),
                dialog.note_text(),
                access_role=self._access_role,
            )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return

        self.feedback_label.show_success("Щоденну перевірку зафіксовано.")
        self.saved.emit()

    def _reissue_record(self) -> None:
        """Готує новий чернетковий наряд на основі поточного.
        Prepares a new draft permit based on the current record.
        """

        if self._read_only:
            self.feedback_label.show_error("Режим read-only: закриття недоступне.")
            return
        if self._current_record is None or self._current_record.record_id is None:
            self.feedback_label.show_error("Створення нового наряду доступне лише для збереженого запису.")
            return

        try:
            self._start_new_record_from_current()
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return

        self._pending_reissue_participants = ()

    def _close_record(self) -> None:
        """Закриває поточний наряд через окрему підтверджену дію.
        Closes the current permit through a dedicated confirmed action.
        """

        if self._current_record is None or self._current_record.record_id is None:
            self.feedback_label.show_error("Закриття доступне лише для збереженого наряду.")
            return

        dialog = CloseWorkPermitDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        try:
            close_work_permit_record(
                self._database_path,
                int(self._current_record.record_id),
                access_role=self._access_role,
            )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return

        self.feedback_label.show_success("Наряд закрито вручну.")
        self.saved.emit()

    def _cancel_record(self) -> None:
        """Скасовує поточний наряд із фіксацією причини.
        Cancels the current permit with a recorded reason.
        """

        if self._read_only:
            self.feedback_label.show_error("Режим read-only: скасування недоступне.")
            return
        if self._current_record is None or self._current_record.record_id is None:
            self.feedback_label.show_error("Скасування доступне лише для збереженого наряду.")
            return

        dialog = CancelWorkPermitDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        try:
            cancel_work_permit_record(
                self._database_path,
                int(self._current_record.record_id),
                dialog.reason_text(),
                access_role=self._access_role,
            )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return

        self.feedback_label.show_success("Наряд скасовано.")
        self.saved.emit()

    def _save_record(self) -> None:
        """Створює або оновлює наряд-допуск через application services.
        Creates or updates a work permit through application services.
        """

        if self._read_only:
            self.feedback_label.show_error("Режим read-only: збереження недоступне.")
            return
        basis_text, basis_note = self.basis_panel.values()
        participants = self._effective_participants()
        try:
            if self._current_record_id is None:
                create_work_permit_record(
                    self._database_path,
                    self.permit_number_input.text(),
                    self.work_kind_input.text(),
                    self.work_location_input.text(),
                    self.starts_at_input.text(),
                    self.ends_at_input.text(),
                    self.responsible_input.text(),
                    self.issuer_input.text(),
                    self.current_employee_personnel_number(),
                    str(self.role_input.currentData() or ""),
                    self.note_input.toPlainText(),
                    str(self.target_training_status_input.currentData() or ""),
                    self.target_training_date_input.text(),
                    self.target_training_conducted_by_input.text(),
                    self.target_training_note_input.toPlainText(),
                    basis_text,
                    basis_note,
                    participants=participants,
                    access_role=self._access_role,
                )
            else:
                update_work_permit_record(
                    self._database_path,
                    self._current_record_id,
                    self.permit_number_input.text(),
                    self.work_kind_input.text(),
                    self.work_location_input.text(),
                    self.starts_at_input.text(),
                    self.ends_at_input.text(),
                    self.responsible_input.text(),
                    self.issuer_input.text(),
                    self.current_employee_personnel_number(),
                    str(self.role_input.currentData() or ""),
                    self.note_input.toPlainText(),
                    str(self.target_training_status_input.currentData() or ""),
                    self.target_training_date_input.text(),
                    self.target_training_conducted_by_input.text(),
                    self.target_training_note_input.toPlainText(),
                    basis_text,
                    basis_note,
                    participants=participants,
                    access_role=self._access_role,
                )
        except ValueError as error:
            self.feedback_label.show_error(str(error))
            return
        self.feedback_label.show_success("Наряд-допуск збережено.")
        self.saved.emit()
