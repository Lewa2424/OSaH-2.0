from dataclasses import dataclass, field

from osah.domain.entities.ai_item_draft import AiItemDraft


@dataclass(frozen=True, slots=True)
class AiSemanticPayload:
    """Данные, которые нужно создать, обновить или подготовить.
    Data to create, update or prepare.
    """

    full_name: str | None = None
    position_name: str | None = None
    department_name: str | None = None
    event_date: str | None = None
    effective_date: str | None = None
    valid_until_date: str | None = None
    training_type: str | None = None
    conducted_by: str | None = None
    topic: str | None = None
    items: tuple[AiItemDraft, ...] = field(default_factory=tuple)
    ppe_item_query: str | None = None
    restriction_note: str | None = None
    replacement_reason: str | None = None
    work_kind: str | None = None
    work_location: str | None = None
    starts_at_text: str | None = None
    ends_at_text: str | None = None
    add_employee_queries: tuple[str, ...] = field(default_factory=tuple)
    remove_employee_queries: tuple[str, ...] = field(default_factory=tuple)
    safety_measures: tuple[str, ...] = field(default_factory=tuple)
