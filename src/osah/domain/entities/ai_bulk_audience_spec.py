from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class AiBulkAudienceSpec:
    """Опис аудиторії для масової AI-команди.
    Audience description for a bulk AI command.
    """

    employee_queries: tuple[str, ...] = field(default_factory=tuple)
    resolved_personnel_numbers: tuple[str, ...] = field(default_factory=tuple)
    department_query: str | None = None
    position_query: str | None = None
    filter_key: str | None = None
    permit_number: str | None = None
    arrived_from: str | None = None
    arrived_until: str | None = None
    combine_mode: str = "and"
