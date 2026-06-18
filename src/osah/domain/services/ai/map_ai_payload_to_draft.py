from osah.domain.entities.ai_employee_field_updates import AiEmployeeFieldUpdates
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_bulk_intent
from osah.domain.services.ai.parse_ai_bulk_audience_spec import parse_ai_bulk_audience_spec
from osah.domain.services.ai.validate_ai_command_draft import normalize_ai_item_drafts


def map_ai_payload_to_draft(command_text: str, payload: dict[str, object], *, source: str = "llm") -> AiCommandDraft:
    """Мапить JSON LLM у чернетку AI-команди.
    Maps LLM JSON payload into an AI command draft.
    """

    raw_intent = str(payload.get("intent", "unknown")).strip()
    try:
        intent = AiIntentKind(raw_intent)
    except ValueError:
        intent = AiIntentKind.UNKNOWN

    employee_field_updates = _parse_employee_field_updates(payload.get("employee_field_updates"))
    bulk_audience_spec = parse_ai_bulk_audience_spec(payload.get("bulk_audience_spec"))
    record_id_raw = payload.get("record_id")
    record_id = int(record_id_raw) if isinstance(record_id_raw, (int, str)) and str(record_id_raw).isdigit() else None

    return AiCommandDraft(
        intent=intent,
        raw_command=command_text.strip(),
        source=source,
        employee_query=_optional_str(payload.get("employee_query")),
        department_query=_optional_str(payload.get("department_query")),
        position_query=_optional_str(payload.get("position_query")),
        personnel_number=_optional_str(payload.get("personnel_number")),
        ppe_item_query=_optional_str(payload.get("ppe_item_query")),
        items=normalize_ai_item_drafts(payload.get("items")),
        issue_date=_optional_str(payload.get("issue_date")),
        section_key=_optional_str(payload.get("section_key")),
        needs_confirmation=bool(payload.get("needs_confirmation", True)),
        training_type=_optional_str(payload.get("training_type")),
        valid_until_date=_optional_str(payload.get("valid_until_date")),
        medical_decision=_optional_str(payload.get("medical_decision")),
        restriction_note=_optional_str(payload.get("restriction_note")),
        replacement_date=_optional_str(payload.get("replacement_date")),
        next_control_date=_optional_str(payload.get("next_control_date")),
        conducted_by=_optional_str(payload.get("conducted_by")),
        record_id=record_id,
        permit_number=_optional_str(payload.get("permit_number")),
        permit_query=_optional_str(payload.get("permit_query")),
        participant_role=_optional_str(payload.get("participant_role")),
        work_kind=_optional_str(payload.get("work_kind")),
        work_location=_optional_str(payload.get("work_location")),
        starts_at_text=_optional_str(payload.get("starts_at_text")),
        ends_at_text=_optional_str(payload.get("ends_at_text")),
        employee_field_updates=employee_field_updates,
        explain_topic=_optional_str(payload.get("explain_topic")),
        module_key=_optional_str(payload.get("module_key")),
        report_scope=_optional_str(payload.get("report_scope")),
        bulk_audience_spec=bulk_audience_spec,
        filter_key=_optional_str(payload.get("filter_key")),
        work_risk_category=_optional_str(payload.get("work_risk_category")),
        use_manual_next_control_date=bool(payload.get("use_manual_next_control_date", False)),
    )


def _optional_str(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _parse_employee_field_updates(raw_value: object) -> AiEmployeeFieldUpdates | None:
    if not isinstance(raw_value, dict):
        return None
    updates = AiEmployeeFieldUpdates(
        position_name=_optional_str(raw_value.get("position_name")),
        department_name=_optional_str(raw_value.get("department_name")),
        employment_status=_optional_str(raw_value.get("employment_status")),
    )
    if not any((updates.position_name, updates.department_name, updates.employment_status)):
        return None
    return updates
