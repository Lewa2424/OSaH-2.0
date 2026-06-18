from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.entities.ai_semantic_audience_spec import AiSemanticAudienceSpec
from osah.domain.entities.ai_semantic_audience_type import AiSemanticAudienceType
from osah.domain.entities.ai_semantic_condition import AiSemanticCondition
from osah.domain.entities.ai_semantic_condition_type import AiSemanticConditionType
from osah.domain.entities.ai_semantic_draft import AiSemanticDraft
from osah.domain.entities.ai_semantic_intent import AiSemanticIntent
from osah.domain.entities.ai_semantic_mode import AiSemanticMode
from osah.domain.entities.ai_semantic_module import AiSemanticModule
from osah.domain.entities.ai_semantic_payload import AiSemanticPayload


def map_ai_semantic_payload_to_draft(
    command_text: str,
    payload: dict[str, object],
) -> AiSemanticDraft:
    """Мапить JSON LLM у семантичний чернетковий опис AI-команди.
    Maps LLM JSON into a semantic AI command draft.
    """

    return AiSemanticDraft(
        intent=_enum_value(AiSemanticIntent, payload.get("intent"), AiSemanticIntent.UNKNOWN),
        raw_command=command_text.strip(),
        module=_enum_value(AiSemanticModule, payload.get("module"), AiSemanticModule.UNKNOWN),
        mode=_enum_value(AiSemanticMode, payload.get("mode"), AiSemanticMode.UNSUPPORTED),
        audience=_parse_audience(payload.get("audience")),
        payload=_parse_payload(payload.get("payload")),
        conditions=_parse_conditions(payload.get("conditions")),
        needs_confirmation=bool(payload.get("needs_confirmation", False)),
        clarification_message=_optional_str(payload.get("clarification_message")),
    )


def _parse_audience(raw_value: object) -> AiSemanticAudienceSpec:
    if not isinstance(raw_value, dict):
        return AiSemanticAudienceSpec()
    return AiSemanticAudienceSpec(
        audience_type=_enum_value(
            AiSemanticAudienceType,
            raw_value.get("type"),
            AiSemanticAudienceType.NONE,
        ),
        employee_queries=_string_tuple(raw_value.get("employee_queries")),
        department_query=_optional_str(raw_value.get("department_query")),
        position_query=_optional_str(raw_value.get("position_query")),
        permit_number=_optional_str(raw_value.get("permit_number")),
        filters=_string_tuple(raw_value.get("filters")),
    )


def _parse_payload(raw_value: object) -> AiSemanticPayload:
    if not isinstance(raw_value, dict):
        return AiSemanticPayload()
    return AiSemanticPayload(
        full_name=_optional_str(raw_value.get("full_name")),
        position_name=_optional_str(raw_value.get("position_name")),
        department_name=_optional_str(raw_value.get("department_name")),
        event_date=_optional_str(raw_value.get("event_date")),
        effective_date=_optional_str(raw_value.get("effective_date")),
        valid_until_date=_optional_str(raw_value.get("valid_until_date")),
        training_type=_optional_str(raw_value.get("training_type")),
        conducted_by=_optional_str(raw_value.get("conducted_by")),
        topic=_optional_str(raw_value.get("topic")),
        items=_parse_items(raw_value.get("items")),
        ppe_item_query=_optional_str(raw_value.get("ppe_item_query")),
        restriction_note=_optional_str(raw_value.get("restriction_note")),
        replacement_reason=_optional_str(raw_value.get("replacement_reason")),
        work_kind=_optional_str(raw_value.get("work_kind")),
        work_location=_optional_str(raw_value.get("work_location")),
        starts_at_text=_optional_str(raw_value.get("starts_at_text")),
        ends_at_text=_optional_str(raw_value.get("ends_at_text")),
        add_employee_queries=_string_tuple(raw_value.get("add_employee_queries")),
        remove_employee_queries=_string_tuple(raw_value.get("remove_employee_queries")),
        safety_measures=_string_tuple(raw_value.get("safety_measures")),
    )


def _parse_items(raw_value: object) -> tuple[AiItemDraft, ...]:
    if not isinstance(raw_value, list):
        return ()
    items: list[AiItemDraft] = []
    for item in raw_value:
        if not isinstance(item, dict):
            continue
        name = _optional_str(item.get("name"))
        if name is None:
            continue
        quantity_raw = item.get("quantity")
        quantity = int(quantity_raw) if isinstance(quantity_raw, (int, str)) and str(quantity_raw).isdigit() else 1
        items.append(AiItemDraft(name=name, quantity=max(1, quantity)))
    return tuple(items)


def _parse_conditions(raw_value: object) -> tuple[AiSemanticCondition, ...]:
    conditions: list[AiSemanticCondition] = []
    for condition in _string_tuple(raw_value):
        condition_type = _enum_value(
            AiSemanticConditionType,
            condition,
            None,
        )
        if condition_type is not None:
            conditions.append(AiSemanticCondition(condition_type=condition_type))
    return tuple(conditions)


def _enum_value(enum_type, raw_value: object, default):
    if not isinstance(raw_value, str):
        return default
    try:
        return enum_type(raw_value.strip())
    except ValueError:
        return default


def _optional_str(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
