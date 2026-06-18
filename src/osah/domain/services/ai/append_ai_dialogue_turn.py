from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_dialogue_turn import AiDialogueTurn


_MAX_TURNS = 8


def append_ai_dialogue_turn(
    state: AiDialogueState | None,
    *,
    role: str,
    text: str,
) -> AiDialogueState:
    """Додає репліку до історії діалогу з обмеженням довжини.
    Appends a turn to dialogue history with length cap.
    """

    normalized_text = text.strip()
    if not normalized_text:
        return state or AiDialogueState()

    base = state or AiDialogueState()
    turns = (*base.turns, AiDialogueTurn(role=role, text=normalized_text))
    if len(turns) > _MAX_TURNS:
        turns = turns[-_MAX_TURNS:]
    return AiDialogueState(
        audience_personnel_numbers=base.audience_personnel_numbers,
        audience_labels=base.audience_labels,
        ppe_item_query=base.ppe_item_query,
        department_query=base.department_query,
        source_intent=base.source_intent,
        pending_kind=base.pending_kind,
        last_answer_intent=base.last_answer_intent,
        last_answer_summary=base.last_answer_summary,
        last_mentioned_personnel_number=base.last_mentioned_personnel_number,
        turns=turns,
    )
