from dataclasses import dataclass, field

from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_employee_field_updates import AiEmployeeFieldUpdates
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft


@dataclass(slots=True)
class AiCommandDraft:
    """Структурований чернетковий план дії AI.
    Structured draft action plan produced by AI parsing.
    """

    intent: AiIntentKind
    raw_command: str
    source: str
    employee_query: str | None = None
    department_query: str | None = None
    position_query: str | None = None
    personnel_number: str | None = None
    items: tuple[AiItemDraft, ...] = field(default_factory=tuple)
    issue_date: str | None = None
    section_key: str | None = None
    ppe_item_query: str | None = None
    needs_confirmation: bool = False
    training_type: str | None = None
    valid_until_date: str | None = None
    medical_decision: str | None = None
    restriction_note: str | None = None
    replacement_date: str | None = None
    next_control_date: str | None = None
    conducted_by: str | None = None
    record_id: int | None = None
    permit_number: str | None = None
    permit_query: str | None = None
    participant_role: str | None = None
    work_kind: str | None = None
    work_location: str | None = None
    starts_at_text: str | None = None
    ends_at_text: str | None = None
    employee_field_updates: AiEmployeeFieldUpdates | None = None
    explain_topic: str | None = None
    module_key: str | None = None
    report_scope: str | None = None
    clarification_message: str | None = None
    bulk_audience_spec: AiBulkAudienceSpec | None = None
    resolved_audience: tuple[str, ...] | None = None
    filter_key: str | None = None
    work_risk_category: str | None = None
    use_manual_next_control_date: bool = False
    work_permit_remove_queries: tuple[str, ...] = field(default_factory=tuple)
    semantic_conditions: tuple[str, ...] = field(default_factory=tuple)
