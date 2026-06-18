from osah.domain.entities.ai_semantic_draft import AiSemanticDraft


def collect_semantic_employee_queries(semantic_draft: AiSemanticDraft) -> tuple[str, ...]:
    """Збирає всі фрагменти ПІБ із semantic draft (audience + payload).
    Collects all employee name fragments from a semantic draft (audience + payload).
    """

    queries: list[str] = []
    seen: set[str] = set()

    def add_query(value: str | None) -> None:
        normalized = (value or "").strip()
        if not normalized:
            return
        key = normalized.lower()
        if key in seen:
            return
        seen.add(key)
        queries.append(normalized)

    for employee_query in semantic_draft.audience.employee_queries:
        add_query(employee_query)

    payload = semantic_draft.payload
    for employee_query in payload.add_employee_queries:
        add_query(employee_query)
    for employee_query in payload.remove_employee_queries:
        add_query(employee_query)
    add_query(payload.full_name)

    return tuple(queries)
