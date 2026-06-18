from dataclasses import dataclass

from osah.domain.entities.ai_semantic_condition_type import AiSemanticConditionType


@dataclass(frozen=True, slots=True)
class AiSemanticCondition:
    """Условие, которое ClearWork обязан проверить перед выполнением.
    Condition ClearWork must check before execution.
    """

    condition_type: AiSemanticConditionType
    note: str = ""
