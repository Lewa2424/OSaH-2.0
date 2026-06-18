from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.command_verb_tokens import (
    filter_valid_employee_query_tokens,
    is_employee_query_stop_word,
)
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_bulk_intent
from osah.domain.services.ai.should_preserve_trusted_semantic_slot import is_trusted_draft_source

_BULK_TO_SINGLE_INTENT = {
    AiIntentKind.BULK_CREATE_PPE_ISSUANCE: AiIntentKind.CREATE_PPE_ISSUANCE,
    AiIntentKind.BULK_CREATE_TRAINING_RECORD: AiIntentKind.CREATE_TRAINING_RECORD,
    AiIntentKind.BULK_CREATE_MEDICAL_RECORD: AiIntentKind.CREATE_MEDICAL_RECORD,
}

_BROAD_BULK_FILTER_KEYS = frozenset({"active", "активн", "активные", "today"})


def demote_single_employee_bulk_draft(draft: AiCommandDraft) -> AiCommandDraft:
    """Знижує trusted bulk до single-write, якщо аудиторія — один працівник.
    Demotes a trusted bulk draft to single-write when the audience is one employee.
    """

    if not is_trusted_draft_source(draft) or not is_ai_bulk_intent(draft.intent):
        return draft

    single_intent = _BULK_TO_SINGLE_INTENT.get(draft.intent)
    if single_intent is None:
        return draft

    spec = draft.bulk_audience_spec
    if spec is None:
        return draft

    if spec.department_query or spec.position_query or spec.permit_number:
        return draft

    filter_key = (spec.filter_key or "").strip().lower()
    if filter_key and filter_key not in _BROAD_BULK_FILTER_KEYS:
        return draft

    valid_queries = tuple(
        query
        for query in spec.employee_queries
        if query.strip() and not is_employee_query_stop_word(query)
    )
    valid_queries = tuple(filter_valid_employee_query_tokens(valid_queries))
    if len(valid_queries) != 1:
        return draft

    employee_query = valid_queries[0]
    trusted_employee = (draft.employee_query or "").strip()
    if trusted_employee and not is_employee_query_stop_word(trusted_employee):
        employee_query = trusted_employee

    return replace(
        draft,
        intent=single_intent,
        employee_query=employee_query,
        bulk_audience_spec=None,
        filter_key=None,
        needs_confirmation=True,
    )
