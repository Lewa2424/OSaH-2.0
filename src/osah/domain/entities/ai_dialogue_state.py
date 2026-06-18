from dataclasses import dataclass, field

from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_dialogue_turn import AiDialogueTurn


@dataclass(slots=True)
class AiDialogueState:
    """Стан діалогу AI для follow-up команд і контексту LLM.
    AI dialogue state for follow-up commands and LLM context.
    """

    audience_personnel_numbers: tuple[str, ...] = field(default_factory=tuple)
    audience_labels: tuple[str, ...] = field(default_factory=tuple)
    ppe_item_query: str | None = None
    department_query: str | None = None
    position_query: str | None = None
    source_intent: str | None = None
    pending_kind: AiConversationPendingKind | None = None
    last_answer_intent: str | None = None
    last_answer_summary: str | None = None
    last_mentioned_personnel_number: str | None = None
    turns: tuple[AiDialogueTurn, ...] = field(default_factory=tuple)

    @property
    def resolved_personnel_numbers(self) -> tuple[str, ...]:
        """Зворотна сумісність із AiConversationContext.
        Backward compatibility with AiConversationContext.
        """

        return self.audience_personnel_numbers
