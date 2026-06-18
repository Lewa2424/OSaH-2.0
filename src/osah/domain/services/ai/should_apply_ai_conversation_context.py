from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.services.ai.convert_ai_dialogue_state import dialogue_state_from_conversation_context
from osah.domain.services.ai.should_apply_ai_dialogue_state import should_apply_ai_dialogue_state


def should_apply_ai_conversation_context(
    context: AiConversationContext | None,
    command_text: str,
) -> bool:
    """Визначає, чи наступна команда має злитись із збереженим контекстом діалогу.
    Decides whether the next command should merge with stored dialogue context.
    """

    return should_apply_ai_dialogue_state(
        dialogue_state_from_conversation_context(context),
        command_text,
    )


def should_apply_dialogue_state(
    state: AiDialogueState | None,
    command_text: str,
) -> bool:
    """Визначає, чи наступна команда має злитись із dialogue state.
    Decides whether the next command should merge with dialogue state.
    """

    return should_apply_ai_dialogue_state(state, command_text)
