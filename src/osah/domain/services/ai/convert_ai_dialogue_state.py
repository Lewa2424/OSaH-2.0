from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.entities.ai_dialogue_state import AiDialogueState


def dialogue_state_from_conversation_context(
    context: AiConversationContext | None,
) -> AiDialogueState | None:
    """Конвертує вузький conversation context у повний dialogue state.
    Converts narrow conversation context into full dialogue state.
    """

    if context is None:
        return None
    return AiDialogueState(
        audience_personnel_numbers=context.resolved_personnel_numbers,
        ppe_item_query=context.ppe_item_query,
        department_query=context.department_query,
        source_intent=context.source_intent,
        pending_kind=context.pending_kind,
    )


def conversation_context_from_dialogue_state(
    state: AiDialogueState | None,
) -> AiConversationContext | None:
    """Конвертує dialogue state у conversation context для зворотної сумісності.
    Converts dialogue state into conversation context for backward compatibility.
    """

    if state is None:
        return None
    return AiConversationContext(
        resolved_personnel_numbers=state.audience_personnel_numbers,
        ppe_item_query=state.ppe_item_query,
        department_query=state.department_query,
        source_intent=state.source_intent,
        pending_kind=state.pending_kind,
    )
