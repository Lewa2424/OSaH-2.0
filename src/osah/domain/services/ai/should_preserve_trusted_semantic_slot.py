from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_bulk_intent, is_ai_write_intent
from osah.domain.services.ai.extract_bulk_audience_from_command import (
    has_bulk_marker_in_command,
    has_implicit_bulk_audience_marker,
    is_department_audience_in_command,
)
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing

TRUSTED_SOURCES = frozenset({"llm", "pattern_memory", "session", "dialogue_state"})

_SINGLE_WRITE_INTENTS = frozenset(
    {
        AiIntentKind.CREATE_PPE_ISSUANCE,
        AiIntentKind.CREATE_TRAINING_RECORD,
        AiIntentKind.CREATE_MEDICAL_RECORD,
        AiIntentKind.UPDATE_PPE_RECORD,
        AiIntentKind.UPDATE_MEDICAL_RECORD,
        AiIntentKind.UPDATE_EMPLOYEE_FIELDS,
        AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT,
    }
)


def is_trusted_draft_source(draft: AiCommandDraft) -> bool:
    """Перевіряє, чи чернетка з довіреного джерела (LLM, сесія, пам'ять).
    Checks whether the draft comes from a trusted source (LLM, session, memory).
    """

    return draft.source in TRUSTED_SOURCES


def should_preserve_trusted_slot(draft: AiCommandDraft, slot: str) -> bool:
    """Чи зберігати слот із довіреного джерела без regex-перезапису.
    Whether to keep a slot from a trusted source without regex overwrite.
    """

    if not is_trusted_draft_source(draft):
        return False

    if slot == "intent":
        return draft.intent in _SINGLE_WRITE_INTENTS

    if slot == "employee_query":
        return bool((draft.employee_query or "").strip())

    if slot == "personnel_number":
        return bool((draft.personnel_number or "").strip())

    if slot == "department_query":
        return bool((draft.department_query or "").strip())

    if slot == "position_query":
        return bool((draft.position_query or "").strip())

    if slot == "issue_date":
        return bool((draft.issue_date or "").strip())

    if slot == "training_type":
        return bool((draft.training_type or "").strip())

    if slot == "work_risk_category":
        return bool((draft.work_risk_category or "").strip())

    if slot == "ppe_item_query":
        return bool((draft.ppe_item_query or "").strip())

    if slot == "items":
        return bool(draft.items)

    if slot == "bulk_audience_spec":
        return (
            draft.bulk_audience_spec is not None
            and has_bulk_audience_narrowing(draft.bulk_audience_spec)
        )

    return False


def should_block_bulk_intent_promotion(draft: AiCommandDraft) -> bool:
    """Чи заборонено підвищувати trusted single-write до bulk під час compile.
    Whether trusted single-write must not be promoted to bulk during compile.
    """

    if not is_trusted_draft_source(draft):
        return False

    if draft.intent == AiIntentKind.UPDATE_MEDICAL_RECORD:
        return True

    raw_command = draft.raw_command.strip()
    if has_bulk_marker_in_command(raw_command) or has_implicit_bulk_audience_marker(raw_command):
        return False
    if is_department_audience_in_command(raw_command, draft.employee_query):
        return False

    if should_preserve_trusted_slot(draft, "intent"):
        if should_preserve_trusted_slot(draft, "employee_query") or should_preserve_trusted_slot(
            draft, "personnel_number"
        ):
            return True

    if is_ai_write_intent(draft.intent) and not is_ai_bulk_intent(draft.intent):
        if should_preserve_trusted_slot(draft, "employee_query") or should_preserve_trusted_slot(
            draft, "personnel_number"
        ):
            return True

    return False
