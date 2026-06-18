from pathlib import Path

from osah.domain.entities.ai_bulk_audience_row import AiBulkAudienceRow
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.detect_duplicate_ppe_issuance import detect_duplicate_ppe_issuance
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.normalize_ai_medical_decision import normalize_ai_medical_decision
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type
from osah.domain.services.find_training_chronology_conflict_reason import find_training_chronology_conflict_reason
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.parse_service_date_text import parse_service_date_text
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_training_records import list_training_records


def collect_ai_bulk_blocking_issues(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
) -> list[str]:
    """Повертає блокуючі помилки масової операції до підтвердження.
    Returns blocking errors for a bulk operation before confirmation.
    """

    issues: list[str] = []
    for personnel_number in personnel_numbers:
        if draft.intent == AiIntentKind.BULK_CREATE_TRAINING_RECORD:
            warning = _training_chronology_warning(database_path, draft, personnel_number)
            if warning:
                issues.append(f"{personnel_number}: {warning}")
        if draft.intent == AiIntentKind.BULK_CREATE_MEDICAL_RECORD:
            medical_warning = _medical_date_warning(draft)
            if medical_warning:
                issues.append(f"{personnel_number}: {medical_warning}")
    return issues


def validate_ai_bulk_operation(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
) -> tuple[AiBulkAudienceRow, ...]:
    """Перевіряє масову операцію до підтвердження; повертає рядки з попередженнями.
    Pre-validates a bulk operation before confirmation; returns rows with warnings.
    """

    rows: list[AiBulkAudienceRow] = []
    for personnel_number in personnel_numbers:
        warning_text = _collect_warnings(database_path, draft, personnel_number)
        full_name = _resolve_full_name(database_path, personnel_number)
        rows.append(
            AiBulkAudienceRow(
                personnel_number=personnel_number,
                full_name=full_name,
                warning_text=warning_text,
            )
        )
    return tuple(rows)


def _collect_warnings(database_path: Path, draft: AiCommandDraft, personnel_number: str) -> str:
    warnings: list[str] = []

    if draft.intent == AiIntentKind.BULK_CREATE_PPE_ISSUANCE:
        for item in draft.items:
            if detect_duplicate_ppe_issuance(
                database_path,
                personnel_number=personnel_number,
                ppe_name=item.name,
                issue_date_text=draft.issue_date,
            ):
                warnings.append(f"можливий дублікат ЗІЗ «{item.name}»")

    if draft.intent == AiIntentKind.BULK_CREATE_TRAINING_RECORD:
        chronology_warning = _training_chronology_warning(database_path, draft, personnel_number)
        if chronology_warning:
            warnings.append(chronology_warning)

    if draft.intent == AiIntentKind.BULK_CREATE_MEDICAL_RECORD:
        medical_warning = _medical_date_warning(draft)
        if medical_warning:
            warnings.append(medical_warning)

    return "; ".join(warnings)


def _training_chronology_warning(database_path: Path, draft: AiCommandDraft, personnel_number: str) -> str:
    try:
        event_date = parse_service_date_text(normalize_ai_issue_date_text(draft.issue_date))
        training_type = TrainingType(normalize_ai_training_type(draft.training_type))
    except ValueError:
        return "некоректні дати або тип інструктажу"

    probe_record = TrainingRecord(
        record_id=None,
        employee_personnel_number=personnel_number,
        employee_full_name="",
        training_type=training_type,
        event_date=event_date.isoformat(),
        next_control_date=event_date.isoformat(),
        conducted_by=(draft.conducted_by or "Інспектор").strip(),
        note_text="",
        status=TrainingStatus.CURRENT,
    )
    connection = create_database_connection(database_path)
    try:
        existing_records = tuple(
            record for record in list_training_records(connection) if record.employee_personnel_number == personnel_number
        )
    finally:
        connection.close()
    conflict = find_training_chronology_conflict_reason(probe_record, existing_records)
    return conflict or ""


def _medical_date_warning(draft: AiCommandDraft) -> str:
    try:
        valid_from = parse_service_date_text(normalize_ai_issue_date_text(draft.issue_date))
        valid_until = parse_service_date_text(
            normalize_ai_issue_date_text(draft.valid_until_date or draft.issue_date)
        )
    except ValueError:
        return "некоректні дати медогляду"
    if valid_until < valid_from:
        return "дата закінчення раніше дати початку"
    if not (draft.medical_decision or "").strip():
        return "не вказано медичне рішення"
    return ""


def _resolve_full_name(database_path: Path, personnel_number: str) -> str:
    from osah.application.services.load_employee_registry import load_employee_registry

    for employee in load_employee_registry(database_path):
        if employee.personnel_number == personnel_number:
            return employee.full_name
    return personnel_number
