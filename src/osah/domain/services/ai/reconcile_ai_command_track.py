from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_track import AiCommandTrack
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.detect_ai_command_track import (
    detect_ai_command_track,
    extract_ppe_token_from_command,
    has_today_date_marker,
    infer_write_module_key,
    matches_section_problems_query,
)
from osah.domain.services.ai.extract_employee_query_from_command import (
    extract_employee_query_from_command,
    extract_personnel_number_from_command,
)
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_answer_intent, is_ai_write_intent
from osah.domain.services.ai.should_preserve_trusted_semantic_slot import should_preserve_trusted_slot


def reconcile_ai_command_track(draft: AiCommandDraft) -> AiCommandDraft:
    """Вирівнює intent із головним рельсом READ/WRITE/NAV.
    Aligns the intent with the detected READ/WRITE/NAV track.
    """

    raw_command = draft.raw_command.strip()
    if not raw_command:
        return draft

    if matches_section_problems_query(raw_command):
        return replace(draft, intent=AiIntentKind.QUERY_SECTION_PROBLEMS)

    track = detect_ai_command_track(draft)
    if track == AiCommandTrack.WRITE:
        return _align_write_track(draft, raw_command)
    if track == AiCommandTrack.READ and is_ai_write_intent(draft.intent):
        return _align_read_track(draft, raw_command)
    return draft


def _align_write_track(draft: AiCommandDraft, raw_command: str) -> AiCommandDraft:
    if is_ai_write_intent(draft.intent) and draft.intent != AiIntentKind.UNKNOWN:
        return _enrich_write_slots(draft, raw_command)

    if not is_ai_answer_intent(draft.intent) and draft.intent not in {
        AiIntentKind.QUERY_MISSING_PPE,
        AiIntentKind.QUERY_EMPLOYEE_READINESS,
        AiIntentKind.UNKNOWN,
    }:
        return draft

    module_key = infer_write_module_key(raw_command, draft)
    if should_preserve_trusted_slot(draft, "employee_query"):
        employee_query = draft.employee_query
    else:
        employee_query = draft.employee_query or extract_employee_query_from_command(raw_command)
    if should_preserve_trusted_slot(draft, "personnel_number"):
        personnel_number = draft.personnel_number
    else:
        personnel_number = draft.personnel_number or extract_personnel_number_from_command(raw_command)
    employee_query, personnel_number = _resolve_employee_reference(employee_query, personnel_number)
    issue_date = draft.issue_date or ("сьогодні" if has_today_date_marker(raw_command) else None)

    if module_key == "ppe":
        ppe_token = draft.ppe_item_query or extract_ppe_token_from_command(raw_command)
        items = draft.items
        if not items and ppe_token:
            items = (AiItemDraft(name=ppe_token, quantity=1),)
        return replace(
            draft,
            intent=AiIntentKind.CREATE_PPE_ISSUANCE,
            employee_query=employee_query,
            personnel_number=personnel_number,
            ppe_item_query=ppe_token,
            items=items,
            issue_date=issue_date,
            needs_confirmation=True,
        )

    if module_key == "trainings":
        return replace(
            draft,
            intent=AiIntentKind.CREATE_TRAINING_RECORD,
            employee_query=employee_query,
            personnel_number=personnel_number,
            issue_date=issue_date,
            needs_confirmation=True,
        )

    if module_key == "medical":
        return replace(
            draft,
            intent=AiIntentKind.CREATE_MEDICAL_RECORD,
            employee_query=employee_query,
            personnel_number=personnel_number,
            issue_date=issue_date,
            needs_confirmation=True,
        )

    return _enrich_write_slots(draft, raw_command)


def _align_read_track(draft: AiCommandDraft, raw_command: str) -> AiCommandDraft:
    if draft.intent == AiIntentKind.CREATE_PPE_ISSUANCE:
        if draft.ppe_item_query or extract_ppe_token_from_command(raw_command):
            return replace(draft, intent=AiIntentKind.QUERY_MISSING_PPE)
    return draft


def _enrich_write_slots(draft: AiCommandDraft, raw_command: str) -> AiCommandDraft:
    if should_preserve_trusted_slot(draft, "employee_query"):
        employee_query = draft.employee_query
    else:
        employee_query = draft.employee_query or extract_employee_query_from_command(raw_command)
    if should_preserve_trusted_slot(draft, "personnel_number"):
        personnel_number = draft.personnel_number
    else:
        personnel_number = draft.personnel_number or extract_personnel_number_from_command(raw_command)
    employee_query, personnel_number = _resolve_employee_reference(employee_query, personnel_number)
    issue_date = draft.issue_date or ("сьогодні" if has_today_date_marker(raw_command) else None)
    updates: dict[str, object] = {"needs_confirmation": True}
    if employee_query and not personnel_number:
        updates["employee_query"] = employee_query
    if personnel_number:
        updates["personnel_number"] = personnel_number
        updates["employee_query"] = None
    if issue_date:
        updates["issue_date"] = issue_date
    if draft.intent == AiIntentKind.CREATE_PPE_ISSUANCE and not draft.items:
        ppe_token = draft.ppe_item_query or extract_ppe_token_from_command(raw_command)
        if ppe_token:
            updates["ppe_item_query"] = ppe_token
            updates["items"] = (AiItemDraft(name=ppe_token, quantity=1),)
    return replace(draft, **updates)


def _resolve_employee_reference(
    employee_query: str | None,
    personnel_number: str | None,
) -> tuple[str | None, str | None]:
    if personnel_number:
        return None, personnel_number.strip()
    if employee_query and employee_query.strip().isdigit():
        return None, employee_query.strip()
    return employee_query, personnel_number
