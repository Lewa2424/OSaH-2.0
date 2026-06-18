from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec


def merge_ai_bulk_audience_specs(
    primary: AiBulkAudienceSpec | None,
    secondary: AiBulkAudienceSpec | None,
) -> AiBulkAudienceSpec | None:
    """Об'єднує дві специфікації bulk-аудиторії; secondary має пріоритет для заповнених полів.
    Merges two bulk audience specs; secondary wins for non-empty fields.
    """

    if primary is None and secondary is None:
        return None
    if primary is None:
        return secondary
    if secondary is None:
        return primary

    employee_queries = _merge_unique_strings(primary.employee_queries, secondary.employee_queries)
    resolved_numbers = _merge_unique_strings(
        primary.resolved_personnel_numbers,
        secondary.resolved_personnel_numbers,
    )
    combine_mode = secondary.combine_mode or primary.combine_mode

    return AiBulkAudienceSpec(
        employee_queries=employee_queries,
        resolved_personnel_numbers=resolved_numbers,
        department_query=secondary.department_query or primary.department_query,
        position_query=secondary.position_query or primary.position_query,
        filter_key=secondary.filter_key or primary.filter_key,
        permit_number=secondary.permit_number or primary.permit_number,
        arrived_from=secondary.arrived_from or primary.arrived_from,
        arrived_until=secondary.arrived_until or primary.arrived_until,
        combine_mode=combine_mode,
    )


def _merge_unique_strings(
    left: tuple[str, ...],
    right: tuple[str, ...],
) -> tuple[str, ...]:
    merged: list[str] = []
    seen: set[str] = set()
    for value in (*left, *right):
        normalized = value.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(normalized)
    return tuple(merged)
