from dataclasses import dataclass, field

from osah.domain.entities.ai_semantic_audience_type import AiSemanticAudienceType


@dataclass(frozen=True, slots=True)
class AiSemanticAudienceSpec:
    """Смысловое описание сотрудников или записей, которых затрагивает команда.
    Semantic description of employees or records affected by a command.
    """

    audience_type: AiSemanticAudienceType = AiSemanticAudienceType.NONE
    employee_queries: tuple[str, ...] = field(default_factory=tuple)
    department_query: str | None = None
    position_query: str | None = None
    permit_number: str | None = None
    filters: tuple[str, ...] = field(default_factory=tuple)
