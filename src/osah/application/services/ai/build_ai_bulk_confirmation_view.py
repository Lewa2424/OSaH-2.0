from pathlib import Path

from osah.domain.entities.ai_bulk_audience_row import AiBulkAudienceRow
from osah.domain.entities.ai_bulk_confirmation_view import AiBulkConfirmationView
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.normalize_ai_medical_decision import normalize_ai_medical_decision
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type
from osah.domain.services.ai.validate_ai_bulk_operation import validate_ai_bulk_operation


def build_ai_bulk_confirmation_view(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
) -> AiBulkConfirmationView:
    """Будує preview масової AI-дії зі списком працівників.
    Builds the bulk AI action preview with the employee list.
    """

    rows = validate_ai_bulk_operation(database_path, draft, personnel_numbers)
    action_summary = _build_action_summary(draft)
    warning_text = _build_warning_text(rows)
    return AiBulkConfirmationView(
        title="Підтвердьте масову дію",
        summary=f"Буде змінено {len(personnel_numbers)} працівників.",
        action_summary=action_summary,
        rows=rows,
        warning_text=warning_text,
    )


def _build_action_summary(draft: AiCommandDraft) -> str:
    if draft.intent == AiIntentKind.BULK_CREATE_PPE_ISSUANCE:
        item_names = ", ".join(item.name for item in draft.items) or draft.ppe_item_query or "ЗІЗ"
        return f"Видача: {item_names} ({normalize_ai_issue_date_text(draft.issue_date)})"
    if draft.intent == AiIntentKind.BULK_CREATE_TRAINING_RECORD:
        return (
            f"Інструктаж: {normalize_ai_training_type(draft.training_type)} "
            f"({normalize_ai_issue_date_text(draft.issue_date)})"
        )
    if draft.intent == AiIntentKind.BULK_CREATE_MEDICAL_RECORD:
        return (
            f"Медогляд: {normalize_ai_medical_decision(draft.medical_decision)} "
            f"({normalize_ai_issue_date_text(draft.issue_date)} — "
            f"{normalize_ai_issue_date_text(draft.valid_until_date or draft.issue_date)})"
        )
    if draft.intent == AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS:
        updates = draft.employee_field_updates
        parts: list[str] = []
        if updates is not None:
            if updates.position_name:
                parts.append(f"посада → {updates.position_name}")
            if updates.department_name:
                parts.append(f"підрозділ → {updates.department_name}")
            if updates.employment_status:
                parts.append(f"статус → {updates.employment_status}")
        return "Оновлення полів: " + (", ".join(parts) if parts else "поля працівника")
    if draft.intent == AiIntentKind.BULK_ADD_WORK_PERMIT_PARTICIPANTS:
        permit_number = draft.permit_number or draft.bulk_audience_spec.permit_number if draft.bulk_audience_spec else ""
        return f"Додати учасників до наряду №{permit_number}"
    return draft.intent.value


def _build_warning_text(rows: tuple[AiBulkAudienceRow, ...]) -> str:
    warning_rows = [row for row in rows if row.warning_text]
    if not warning_rows:
        return ""
    return f"Є попередження для {len(warning_rows)} працівників. Перевірте список перед підтвердженням."
