from pathlib import Path

from osah.application.services.change_work_permit_participants import change_work_permit_participants
from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.create_training_record import create_training_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.update_employee import update_employee
from osah.application.services.update_medical_record import update_medical_record
from osah.application.services.update_ppe_record import update_ppe_record
from osah.application.services.update_training_record import update_training_record
from osah.application.services.ai.resolve_ai_record_for_update import resolve_ai_record_for_update
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.services.ai.ensure_ai_intent_is_allowed import ensure_ai_intent_is_allowed
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.normalize_ai_medical_decision import normalize_ai_medical_decision
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type


def execute_confirmed_ai_command(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    resolved_personnel_number: str | None = None,
    access_role: AccessRole,
) -> str:
    """Виконує підтверджену AI-команду через штатні use cases.
    Executes a confirmed AI command through standard use cases.
    """

    ensure_ai_intent_is_allowed(draft.intent)
    personnel_number = (resolved_personnel_number or draft.personnel_number or "").strip()

    if draft.intent == AiIntentKind.CREATE_PPE_ISSUANCE:
        return _execute_create_ppe(database_path, draft, personnel_number, access_role=access_role)
    if draft.intent == AiIntentKind.CREATE_TRAINING_RECORD:
        return _execute_create_training(database_path, draft, personnel_number, access_role=access_role)
    if draft.intent == AiIntentKind.CREATE_MEDICAL_RECORD:
        return _execute_create_medical(database_path, draft, personnel_number, access_role=access_role)
    if draft.intent == AiIntentKind.UPDATE_PPE_RECORD:
        return _execute_update_ppe(database_path, draft, personnel_number, access_role=access_role)
    if draft.intent == AiIntentKind.UPDATE_TRAINING_RECORD:
        return _execute_update_training(database_path, draft, personnel_number, access_role=access_role)
    if draft.intent == AiIntentKind.UPDATE_MEDICAL_RECORD:
        return _execute_update_medical(database_path, draft, personnel_number, access_role=access_role)
    if draft.intent == AiIntentKind.UPDATE_EMPLOYEE_FIELDS:
        return _execute_update_employee_fields(database_path, draft, personnel_number, access_role=access_role)
    if draft.intent == AiIntentKind.CREATE_WORK_PERMIT_DRAFT:
        return _execute_create_work_permit_draft(database_path, draft, access_role=access_role)
    if draft.intent == AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT:
        return _execute_change_work_permit_participant(database_path, draft, personnel_number, add=True, access_role=access_role)
    if draft.intent == AiIntentKind.REMOVE_WORK_PERMIT_PARTICIPANT:
        return _execute_change_work_permit_participant(database_path, draft, personnel_number, add=False, access_role=access_role)

    raise ValueError(f"Intent '{draft.intent.value}' не підтримує виконання.")


def _execute_create_ppe(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    access_role: AccessRole,
) -> str:
    issue_date_text = normalize_ai_issue_date_text(draft.issue_date)
    replacement_date_text = normalize_ai_issue_date_text(draft.replacement_date or draft.issue_date)
    for item in draft.items:
        create_ppe_record(
            database_path,
            employee_personnel_number=personnel_number,
            ppe_name=item.name,
            is_required=True,
            is_issued=True,
            issue_date_text=issue_date_text,
            replacement_date_text=replacement_date_text,
            quantity_text=str(item.quantity),
            note_text="Створено через ClearWork AI.",
            access_role=access_role,
        )
    return f"Створено {len(draft.items)} запис(ів) ЗІЗ."


def _execute_create_training(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    access_role: AccessRole,
) -> str:
    create_training_record(
        database_path,
        employee_personnel_number=personnel_number,
        training_type=normalize_ai_training_type(draft.training_type),
        event_date_text=normalize_ai_issue_date_text(draft.issue_date),
        next_control_date_text=normalize_ai_issue_date_text(draft.next_control_date) if draft.next_control_date else "",
        conducted_by=(draft.conducted_by or "Інспектор").strip(),
        note_text="Створено через ClearWork AI.",
        work_risk_category=(draft.work_risk_category or "not_applicable").strip(),
        use_manual_next_control_date=draft.use_manual_next_control_date,
        access_role=access_role,
    )
    return "Створено запис інструктажу."


def _execute_create_medical(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    access_role: AccessRole,
) -> str:
    valid_from_text = normalize_ai_issue_date_text(draft.issue_date)
    valid_until_text = normalize_ai_issue_date_text(draft.valid_until_date or draft.issue_date)
    create_medical_record(
        database_path,
        employee_personnel_number=personnel_number,
        valid_from_text=valid_from_text,
        valid_until_text=valid_until_text,
        medical_decision=normalize_ai_medical_decision(draft.medical_decision),
        restriction_note=(draft.restriction_note or "Створено через ClearWork AI.").strip(),
        access_role=access_role,
    )
    return "Створено медичний запис."


def _execute_update_ppe(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    access_role: AccessRole,
) -> str:
    target = resolve_ai_record_for_update(database_path, draft, personnel_number=personnel_number)
    if target is None or target.ppe_record is None:
        raise ValueError("Запис ЗІЗ для оновлення не знайдено.")
    record = target.ppe_record
    issue_date_text = normalize_ai_issue_date_text(draft.issue_date or record.issue_date)
    replacement_date_text = normalize_ai_issue_date_text(draft.replacement_date or draft.issue_date or record.replacement_date)
    update_ppe_record(
        database_path,
        record_id=int(target.record_id),
        employee_personnel_number=personnel_number,
        ppe_name=record.ppe_name,
        is_required=record.is_required,
        is_issued=True,
        issue_date_text=issue_date_text,
        replacement_date_text=replacement_date_text,
        quantity_text=str(record.quantity),
        note_text="Оновлено через ClearWork AI.",
        provision_status=record.provision_status.value,
        compliance_check_state=record.compliance_check_state.value,
        basis_text=record.basis_text,
        basis_note=record.basis_note,
        access_role=access_role,
    )
    return f"Оновлено запис ЗІЗ «{record.ppe_name}»."


def _execute_update_training(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    access_role: AccessRole,
) -> str:
    target = resolve_ai_record_for_update(database_path, draft, personnel_number=personnel_number)
    if target is None or target.training_record is None:
        raise ValueError("Запис інструктажу для оновлення не знайдено.")
    record = target.training_record
    update_training_record(
        database_path,
        record_id=int(target.record_id),
        employee_personnel_number=personnel_number,
        training_type=normalize_ai_training_type(draft.training_type or record.training_type.value),
        event_date_text=normalize_ai_issue_date_text(draft.issue_date or record.event_date),
        next_control_date_text=normalize_ai_issue_date_text(draft.next_control_date) if draft.next_control_date else record.next_control_date,
        conducted_by=(draft.conducted_by or record.conducted_by).strip(),
        note_text="Оновлено через ClearWork AI.",
        person_category=record.person_category.value,
        requires_primary_on_workplace=record.requires_primary_on_workplace,
        work_risk_category=record.work_risk_category.value,
        knowledge_check_result=record.knowledge_check_result.value,
        work_admission_status=record.work_admission_status.value,
        knowledge_check_note=record.knowledge_check_note,
        basis_text=record.basis_text,
        basis_note=record.basis_note,
        access_role=access_role,
    )
    return "Оновлено запис інструктажу."


def _execute_update_medical(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    access_role: AccessRole,
) -> str:
    target = resolve_ai_record_for_update(database_path, draft, personnel_number=personnel_number)
    if target is None or target.medical_record is None:
        raise ValueError("Медичний запис для оновлення не знайдено.")
    record = target.medical_record
    if draft.valid_until_date and not draft.issue_date:
        valid_from_text = record.valid_from
        valid_until_text = normalize_ai_issue_date_text(draft.valid_until_date)
    elif draft.valid_until_date:
        valid_from_text = normalize_ai_issue_date_text(draft.issue_date) if draft.issue_date else record.valid_from
        valid_until_text = normalize_ai_issue_date_text(draft.valid_until_date)
    elif draft.issue_date:
        valid_from_text = normalize_ai_issue_date_text(draft.issue_date)
        valid_until_text = record.valid_until
    else:
        valid_from_text = record.valid_from
        valid_until_text = record.valid_until
    update_medical_record(
        database_path,
        record_id=int(target.record_id),
        employee_personnel_number=personnel_number,
        valid_from_text=valid_from_text,
        valid_until_text=valid_until_text,
        medical_decision=normalize_ai_medical_decision(draft.medical_decision or record.medical_decision.value),
        restriction_note=(draft.restriction_note or record.restriction_note).strip(),
        medical_exam_basis=record.medical_exam_basis.value,
        basis_text=record.basis_text,
        basis_note=record.basis_note,
        access_role=access_role,
    )
    return "Оновлено медичний запис."


def _execute_update_employee_fields(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    access_role: AccessRole,
) -> str:
    employee = next((item for item in load_employee_registry(database_path) if item.personnel_number == personnel_number), None)
    if employee is None:
        raise ValueError("Працівника не знайдено.")
    updates = draft.employee_field_updates
    if updates is None:
        raise ValueError("Немає полів для оновлення.")
    update_employee(
        database_path,
        personnel_number=personnel_number,
        full_name=employee.full_name,
        department_name=updates.department_name or employee.department_name,
        position_name=updates.position_name or employee.position_name,
        employment_status=updates.employment_status or employee.employment_status,
        access_role=access_role,
    )
    return "Оновлено картку працівника."


def _execute_create_work_permit_draft(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    access_role: AccessRole,
) -> str:
    permit_number = (draft.permit_number or draft.permit_query or "").strip()
    participants: tuple[WorkPermitParticipant, ...] = ()
    if draft.bulk_audience_spec is not None and draft.bulk_audience_spec.resolved_personnel_numbers:
        participants = tuple(
            WorkPermitParticipant(
                employee_personnel_number=personnel_number,
                employee_full_name="",
                participant_role=WorkPermitParticipantRole.TEAM_MEMBER,
            )
            for personnel_number in draft.bulk_audience_spec.resolved_personnel_numbers
        )
    create_work_permit_record(
        database_path,
        permit_number=permit_number,
        work_kind=(draft.work_kind or "Роботи").strip(),
        work_location=(draft.work_location or "Місце робіт").strip(),
        starts_at_text=(draft.starts_at_text or "сьогодні 08:00").strip(),
        ends_at_text=(draft.ends_at_text or "сьогодні 17:00").strip(),
        responsible_person="Інспектор",
        issuer_person="Інспектор",
        employee_personnel_number=participants[0].employee_personnel_number if participants else "",
        participant_role=WorkPermitParticipantRole.EXECUTOR.value,
        note_text=(draft.restriction_note or "Створено через ClearWork AI.").strip(),
        participants=participants or None,
        access_role=access_role,
    )
    return f"Створено чернетку наряду №{permit_number}."


def _execute_change_work_permit_participant(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_number: str,
    *,
    add: bool,
    access_role: AccessRole,
) -> str:
    permit_number = (draft.permit_number or draft.permit_query or "").strip()
    permit = next(
        (item for item in load_work_permit_registry(database_path) if item.permit_number.strip() == permit_number),
        None,
    )
    if permit is None or permit.record_id is None:
        raise ValueError("Наряд не знайдено.")

    employee_matches = search_employees_by_query(database_path, personnel_number)
    employee_name = employee_matches[0].full_name if employee_matches else personnel_number
    role = WorkPermitParticipantRole((draft.participant_role or WorkPermitParticipantRole.TEAM_MEMBER.value).strip())

    participants = list(permit.participants)
    if add:
        if any(item.employee_personnel_number == personnel_number for item in participants):
            raise ValueError("Учасник уже є в наряді.")
        participants.append(
            WorkPermitParticipant(
                employee_personnel_number=personnel_number,
                employee_full_name=employee_name,
                participant_role=role,
            )
        )
        action_label = "додано"
    else:
        updated = [item for item in participants if item.employee_personnel_number != personnel_number]
        if len(updated) == len(participants):
            raise ValueError("Учасника не знайдено в наряді.")
        participants = updated
        action_label = "прибрано"

    change_work_permit_participants(
        database_path,
        record_id=int(permit.record_id),
        participants=tuple(participants),
        access_role=access_role,
    )
    return f"Учасника {action_label} з наряду №{permit_number}."


def build_employee_label(database_path: Path, personnel_number: str) -> str:
    """Повертає підпис працівника для confirm-діалогу.
    Returns an employee label for the confirmation dialog.
    """

    matches = search_employees_by_query(database_path, personnel_number)
    if not matches:
        return personnel_number
    employee = matches[0]
    return f"{employee.full_name}, таб. №{employee.personnel_number}"
