from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec


def parse_ai_bulk_audience_spec(raw_value: object) -> AiBulkAudienceSpec | None:
    """Парсить bulk_audience_spec із JSON LLM.
    Parses bulk_audience_spec from LLM JSON.
    """

    if not isinstance(raw_value, dict):
        return None

    employee_queries = _parse_string_tuple(raw_value.get("employee_queries"))
    resolved_personnel_numbers = _parse_string_tuple(raw_value.get("resolved_personnel_numbers"))
    combine_mode = _optional_str(raw_value.get("combine_mode")) or "and"
    if combine_mode not in {"and", "or"}:
        combine_mode = "and"

    spec = AiBulkAudienceSpec(
        employee_queries=employee_queries,
        resolved_personnel_numbers=resolved_personnel_numbers,
        department_query=_optional_str(raw_value.get("department_query")),
        position_query=_optional_str(raw_value.get("position_query")),
        filter_key=_optional_str(raw_value.get("filter_key")),
        permit_number=_optional_str(raw_value.get("permit_number")),
        arrived_from=_optional_str(raw_value.get("arrived_from")),
        arrived_until=_optional_str(raw_value.get("arrived_until")),
        combine_mode=combine_mode,
    )
    if not any(
        (
            spec.employee_queries,
            spec.resolved_personnel_numbers,
            spec.department_query,
            spec.position_query,
            spec.filter_key,
            spec.permit_number,
            spec.arrived_from,
            spec.arrived_until,
        )
    ):
        return None
    return spec


def _optional_str(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _parse_string_tuple(raw_value: object) -> tuple[str, ...]:
    if not isinstance(raw_value, list):
        return ()
    values: list[str] = []
    for item in raw_value:
        if isinstance(item, str) and item.strip():
            values.append(item.strip())
    return tuple(values)
