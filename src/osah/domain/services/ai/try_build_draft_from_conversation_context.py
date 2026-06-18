from pathlib import Path

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.services.ai.convert_ai_dialogue_state import dialogue_state_from_conversation_context
from osah.domain.services.ai.try_build_draft_from_dialogue_state import try_build_draft_from_dialogue_state


def try_build_draft_from_conversation_context(
    command_text: str,
    context: AiConversationContext | None,
    *,
    database_path: Path | None = None,
) -> AiCommandDraft | None:
    """Будує чернетку з контексту діалогу для follow-up команд.
    Builds a command draft from dialogue context for follow-up commands.
    """

    return try_build_draft_from_dialogue_state(
        command_text,
        dialogue_state_from_conversation_context(context),
        database_path=database_path,
    )
