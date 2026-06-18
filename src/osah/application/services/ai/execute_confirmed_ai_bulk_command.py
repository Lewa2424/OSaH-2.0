from pathlib import Path

from osah.application.services.add_work_permit_participants_batch import add_work_permit_participants_batch
from osah.application.services.change_work_permit_participants import change_work_permit_participants
from osah.application.services.create_medical_records_batch import create_medical_records_batch
from osah.application.services.create_ppe_records_batch import create_ppe_records_batch
from osah.application.services.create_training_records_batch import create_training_records_batch
from osah.application.services.update_employee_fields_batch import update_employee_fields_batch
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.ensure_ai_intent_is_allowed import ensure_ai_intent_is_allowed, is_ai_bulk_intent
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.normalize_ai_medical_decision import normalize_ai_medical_decision
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type


def execute_confirmed_ai_bulk_command(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    personnel_numbers: tuple[str, ...],
    access_role: AccessRole,
) -> str:
    """Виконує підтверджену масову AI-команду.
    Executes a confirmed bulk AI command.
    """

    ensure_ai_intent_is_allowed(draft.intent)
    if not is_ai_bulk_intent(draft.intent):
        raise ValueError(f"Intent '{draft.intent.value}' не є масовою дією.")
    if not personnel_numbers:
        raise ValueError("Порожня аудиторія для масової дії.")

    if draft.intent == AiIntentKind.BULK_CREATE_TRAINING_RECORD:
        return _execute_bulk_training(database_path, draft, personnel_numbers, access_role=access_role)
    if draft.intent == AiIntentKind.BULK_CREATE_PPE_ISSUANCE:
        return _execute_bulk_ppe(database_path, draft, personnel_numbers, access_role=access_role)
    if draft.intent == AiIntentKind.BULK_CREATE_MEDICAL_RECORD:
        return _execute_bulk_medical(database_path, draft, personnel_numbers, access_role=access_role)
    if draft.intent == AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS:
        return _execute_bulk_employee_fields(database_path, draft, personnel_numbers, access_role=access_role)
    if draft.intent == AiIntentKind.BULK_ADD_WORK_PERMIT_PARTICIPANTS:
        return _execute_bulk_permit_participants(database_path, draft, personnel_numbers, access_role=access_role)

    raise ValueError(f"Intent '{draft.intent.value}' не підтримує масове виконання.")


def _execute_bulk_training(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
    *,
    access_role: AccessRole,
) -> str:
    create_training_records_batch(
        database_path,
        employee_personnel_numbers=personnel_numbers,
        training_type=normalize_ai_training_type(draft.training_type),
        event_date_text=normalize_ai_issue_date_text(draft.issue_date),
        next_control_date_text=normalize_ai_issue_date_text(draft.next_control_date) if draft.next_control_date else "",
        conducted_by=(draft.conducted_by or "Інспектор").strip(),
        note_text="Створено через ClearWork AI (масово).",
        use_manual_next_control_date=bool(draft.next_control_date),
        access_role=access_role,
    )
    return f"Створено інструктажі для {len(personnel_numbers)} працівників."


def _execute_bulk_ppe(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
    *,
    access_role: AccessRole,
) -> str:
    if not draft.items:
        raise ValueError("Потрібно вказати предмет ЗІЗ.")
    issue_date_text = normalize_ai_issue_date_text(draft.issue_date)
    replacement_date_text = normalize_ai_issue_date_text(draft.replacement_date or draft.issue_date)
    created_total = 0
    for item in draft.items:
        created_total += create_ppe_records_batch(
            database_path,
            employee_personnel_numbers=personnel_numbers,
            ppe_name=item.name,
            quantity_text=str(item.quantity),
            issue_date_text=issue_date_text,
            replacement_date_text=replacement_date_text,
            note_text="Створено через ClearWork AI (масово).",
            access_role=access_role,
        )
    return f"Видано {created_total} запис(ів) ЗІЗ."


def _execute_bulk_medical(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
    *,
    access_role: AccessRole,
) -> str:
    count = create_medical_records_batch(
        database_path,
        employee_personnel_numbers=personnel_numbers,
        valid_from_text=normalize_ai_issue_date_text(draft.issue_date),
        valid_until_text=normalize_ai_issue_date_text(draft.valid_until_date or draft.issue_date),
        medical_decision=normalize_ai_medical_decision(draft.medical_decision),
        restriction_note=(draft.restriction_note or "").strip(),
        access_role=access_role,
    )
    return f"Створено медогляди для {count} працівників."


def _execute_bulk_employee_fields(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
    *,
    access_role: AccessRole,
) -> str:
    if draft.employee_field_updates is None:
        raise ValueError("Потрібно вказати поля для оновлення.")
    count = update_employee_fields_batch(
        database_path,
        employee_personnel_numbers=personnel_numbers,
        field_updates=draft.employee_field_updates,
        access_role=access_role,
    )
    return f"Оновлено поля для {count} працівників."


def _execute_bulk_permit_participants(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
    *,
    access_role: AccessRole,
) -> str:
    permit_number = draft.permit_number
    if not permit_number and draft.bulk_audience_spec is not None:
        permit_number = draft.bulk_audience_spec.permit_number
    if not permit_number:
        raise ValueError("Потрібен номер наряду.")

    messages: list[str] = []
    if personnel_numbers:
        count = add_work_permit_participants_batch(
            database_path,
            permit_number=permit_number,
            employee_personnel_numbers=personnel_numbers,
            participant_role=(draft.participant_role or "worker").strip(),
            access_role=access_role,
        )
        messages.append(f"Додано {count} учасників до наряду.")

    if draft.work_permit_remove_queries:
        removed = _remove_work_permit_participants_by_queries(
            database_path,
            permit_number=permit_number,
            employee_queries=draft.work_permit_remove_queries,
            access_role=access_role,
        )
        messages.append(f"Прибрано {removed} учасників з наряду.")

    if not messages:
        raise ValueError("Немає учасників для зміни в наряді.")
    return " ".join(messages)


def _remove_work_permit_participants_by_queries(
    database_path: Path,
    *,
    permit_number: str,
    employee_queries: tuple[str, ...],
    access_role: AccessRole,
) -> int:
    permit = next(
        (item for item in load_work_permit_registry(database_path) if item.permit_number.strip() == permit_number.strip()),
        None,
    )
    if permit is None or permit.record_id is None:
        raise ValueError("Наряд не знайдено.")

    remove_numbers: set[str] = set()
    for query in employee_queries:
        matches = search_employees_by_query(database_path, query)
        if len(matches) == 1:
            remove_numbers.add(matches[0].personnel_number)

    if not remove_numbers:
        return 0

    participants = [
        participant
        for participant in permit.participants
        if participant.employee_personnel_number not in remove_numbers
    ]
    change_work_permit_participants(
        database_path,
        permit.record_id,
        participants,
        access_role=access_role,
    )
    return len(remove_numbers)
