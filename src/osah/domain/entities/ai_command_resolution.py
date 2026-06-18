from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.entities.ai_navigation_target import AiNavigationTarget


@dataclass(slots=True)
class AiCommandResolution:
    """Результат розбору команди користувача.
    Result of parsing a user command through AI pipeline.
    """

    status: AiCommandResolutionStatus
    message: str = ""
    draft: AiCommandDraft | None = None
    answer_text: str = ""
    follow_up_navigation: AiNavigationTarget | None = None
    allow_copy: bool = False
    trace_id: str | None = None
    session: AiCommandSession | None = None
    next_conversation_context: AiConversationContext | None = None
    next_dialogue_state: AiDialogueState | None = None
    entity_choices: tuple[AiEntityChoice, ...] = field(default_factory=tuple)
    pending_grounding_choice_kind: str | None = None
