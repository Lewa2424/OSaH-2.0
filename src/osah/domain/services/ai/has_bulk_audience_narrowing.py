from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec

_BROAD_FILTER_KEYS = frozenset({"active", "активн", "активные"})


def has_bulk_audience_narrowing(spec: AiBulkAudienceSpec) -> bool:
    """Перевіряє, чи аудиторія достатньо звужена для масової дії.
    Checks whether the bulk audience has enough narrowing criteria.
    """

    if spec.resolved_personnel_numbers or spec.employee_queries:
        return True
    if spec.department_query or spec.position_query or spec.permit_number:
        return True
    if spec.arrived_from or spec.arrived_until:
        return True
    if spec.filter_key and spec.filter_key.strip().lower() not in _BROAD_FILTER_KEYS:
        return True
    return False
