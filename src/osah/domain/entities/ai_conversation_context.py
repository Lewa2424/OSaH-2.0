from dataclasses import dataclass, field

from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind


@dataclass(slots=True)
class AiConversationContext:
    """Контекст попереднього read-запиту для наступних команд у чаті.
    Context of the previous read query for follow-up chat commands.
    """

    resolved_personnel_numbers: tuple[str, ...] = field(default_factory=tuple)
    ppe_item_query: str | None = None
    source_intent: str | None = None
    department_query: str | None = None
    pending_kind: AiConversationPendingKind | None = None
