from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.extract_department_module_status_query import extract_department_module_status_query
from osah.domain.services.ai.matches_department_employees_query import extract_department_employees_query


def try_match_department_employees_query(command_text: str) -> AiCommandDraft | None:
    """Повертає запит списку працівників підрозділу без зайвого уточнення.
    Returns a department employee list query without redundant clarification.
    """

    if extract_department_module_status_query(command_text) is not None:
        return None

    department_query = extract_department_employees_query(command_text)
    if department_query is None:
        return None

    return AiCommandDraft(
        intent=AiIntentKind.QUERY_EMPLOYEES_FILTER,
        raw_command=command_text.strip(),
        source="rule_router",
        filter_key="department",
        department_query=department_query,
        employee_query=department_query,
        needs_confirmation=False,
    )
