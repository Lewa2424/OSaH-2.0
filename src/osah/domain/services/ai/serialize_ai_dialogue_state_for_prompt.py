import json

from osah.domain.entities.ai_dialogue_state import AiDialogueState


def serialize_ai_dialogue_state_for_prompt(state: AiDialogueState | None) -> str:
    """Серіалізує стан діалогу в JSON для LLM prompt.
    Serializes dialogue state into JSON for an LLM prompt.
    """

    if state is None:
        return ""

    payload: dict[str, object] = {
        "last_answer_intent": state.last_answer_intent,
        "last_answer_summary": state.last_answer_summary,
        "audience_personnel_numbers": list(state.audience_personnel_numbers),
        "audience_labels": list(state.audience_labels[:20]),
        "ppe_item_query": state.ppe_item_query,
        "department_query": state.department_query,
        "position_query": state.position_query,
        "source_intent": state.source_intent,
        "pending_kind": state.pending_kind.value if state.pending_kind else None,
        "last_mentioned_personnel_number": state.last_mentioned_personnel_number,
        "recent_turns": [{"role": turn.role, "text": turn.text[:400]} for turn in state.turns[-6:]],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
