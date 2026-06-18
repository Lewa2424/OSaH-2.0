from dataclasses import dataclass, field

from osah.domain.entities.ai_semantic_audience_spec import AiSemanticAudienceSpec
from osah.domain.entities.ai_semantic_condition import AiSemanticCondition
from osah.domain.entities.ai_semantic_intent import AiSemanticIntent
from osah.domain.entities.ai_semantic_mode import AiSemanticMode
from osah.domain.entities.ai_semantic_module import AiSemanticModule
from osah.domain.entities.ai_semantic_payload import AiSemanticPayload


@dataclass(frozen=True, slots=True)
class AiSemanticDraft:
    """Смысловой черновик AI-команды между LLM и строгой логикой ClearWork.
    Semantic AI command draft between the LLM and strict ClearWork logic.
    """

    intent: AiSemanticIntent
    raw_command: str
    module: AiSemanticModule = AiSemanticModule.UNKNOWN
    mode: AiSemanticMode = AiSemanticMode.UNSUPPORTED
    audience: AiSemanticAudienceSpec = field(default_factory=AiSemanticAudienceSpec)
    payload: AiSemanticPayload = field(default_factory=AiSemanticPayload)
    conditions: tuple[AiSemanticCondition, ...] = field(default_factory=tuple)
    needs_confirmation: bool = False
    clarification_message: str | None = None
