from pathlib import Path

from osah.application.services.ai.query_employees_by_department import query_employees_by_department
from osah.application.services.ai.query_employees_missing_ppe import query_employees_missing_ppe
from osah.application.services.ai.ground_ai_command_draft import effective_department_query
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.normalize_ppe_item_query import normalize_ppe_item_query


def build_ai_conversation_context_from_answer(
    database_path: Path,
    draft: AiCommandDraft,
) -> AiConversationContext | None:
    """Зберігає аудиторію з read-відповіді для наступних команд у чаті.
    Stores the audience from a read answer for subsequent chat commands.
    """

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE:
        ppe_item_query = normalize_ppe_item_query((draft.ppe_item_query or "").strip())
        if not ppe_item_query:
            return None
        rows = query_employees_missing_ppe(database_path, ppe_item_query)
        if not rows:
            return None
        return AiConversationContext(
            resolved_personnel_numbers=tuple(row.personnel_number for row in rows),
            ppe_item_query=ppe_item_query,
            source_intent=draft.intent.value,
        )

    if draft.intent == AiIntentKind.QUERY_EMPLOYEES_FILTER and (draft.filter_key or "").strip().lower() == "department":
        department_query = effective_department_query(draft) or ""
        if not department_query:
            return None
        rows = query_employees_by_department(database_path, department_query)
        if not rows:
            return None
        return AiConversationContext(
            resolved_personnel_numbers=tuple(row.personnel_number for row in rows),
            department_query=department_query,
            source_intent=draft.intent.value,
            pending_kind=AiConversationPendingKind.DEPARTMENT_EMPLOYEES,
        )

    return None
