from dataclasses import dataclass
from pathlib import Path

from osah.application.services.ai.ground_ai_command_draft import effective_department_query
from osah.application.services.ai.query_employees_by_department import query_employees_by_department
from osah.application.services.ai.query_employees_missing_ppe import query_employees_missing_ppe
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.append_ai_dialogue_turn import append_ai_dialogue_turn
from osah.domain.services.ai.normalize_ppe_item_query import normalize_ppe_item_query


def build_ai_dialogue_state_from_answer(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    answer_text: str,
    previous_state: AiDialogueState | None = None,
) -> AiDialogueState | None:
    """Оновлює стан діалогу після read-відповіді асистента.
    Updates dialogue state after an assistant read answer.
    """

    base = previous_state or AiDialogueState()
    summary = answer_text.strip()[:500] if answer_text.strip() else None
    intent_value = draft.intent.value

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE:
        ppe_item_query = normalize_ppe_item_query((draft.ppe_item_query or "").strip())
        if not ppe_item_query:
            return None
        rows = query_employees_missing_ppe(
            database_path,
            ppe_item_query,
            department_query=effective_department_query(draft),
            position_query=(draft.position_query or "").strip() or None,
        )
        if not rows:
            return None
        state = AiDialogueState(
            audience_personnel_numbers=tuple(row.personnel_number for row in rows),
            audience_labels=tuple(row.full_name for row in rows),
            ppe_item_query=ppe_item_query,
            department_query=effective_department_query(draft),
            position_query=(draft.position_query or "").strip() or None,
            source_intent=intent_value,
            last_answer_intent=intent_value,
            last_answer_summary=summary,
            turns=base.turns,
        )
        return append_ai_dialogue_turn(state, role="assistant", text=answer_text)

    if draft.intent == AiIntentKind.QUERY_EMPLOYEES_FILTER and (draft.filter_key or "").strip().lower() == "department":
        department_query = effective_department_query(draft) or ""
        if not department_query:
            return None
        rows = query_employees_by_department(database_path, department_query)
        if not rows:
            return None
        state = AiDialogueState(
            audience_personnel_numbers=tuple(row.personnel_number for row in rows),
            audience_labels=tuple(row.full_name for row in rows),
            department_query=department_query,
            source_intent=intent_value,
            pending_kind=AiConversationPendingKind.DEPARTMENT_EMPLOYEES,
            last_answer_intent=intent_value,
            last_answer_summary=summary,
            turns=base.turns,
        )
        return append_ai_dialogue_turn(state, role="assistant", text=answer_text)

    if draft.intent == AiIntentKind.QUERY_MODULE_STATUS and effective_department_query(draft):
        department_query = effective_department_query(draft) or ""
        rows = query_employees_by_department(database_path, department_query)
        if rows:
            state = AiDialogueState(
                audience_personnel_numbers=tuple(row.personnel_number for row in rows),
                audience_labels=tuple(row.full_name for row in rows),
                department_query=department_query,
                source_intent=intent_value,
                pending_kind=AiConversationPendingKind.DEPARTMENT_EMPLOYEES,
                last_answer_intent=intent_value,
                last_answer_summary=summary,
                turns=base.turns,
            )
            return append_ai_dialogue_turn(state, role="assistant", text=answer_text)

    if summary:
        updated = AiDialogueState(
            audience_personnel_numbers=base.audience_personnel_numbers,
            audience_labels=base.audience_labels,
            ppe_item_query=base.ppe_item_query,
            department_query=base.department_query,
            source_intent=base.source_intent,
            pending_kind=base.pending_kind,
            last_answer_intent=intent_value,
            last_answer_summary=summary,
            last_mentioned_personnel_number=base.last_mentioned_personnel_number,
            turns=base.turns,
        )
        return append_ai_dialogue_turn(updated, role="assistant", text=answer_text)

    return None
