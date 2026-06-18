from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.extract_module_status_query_from_command import (
    extract_module_status_query_from_command,
)
from osah.domain.services.ai.try_match_intent_skeleton_command import try_match_intent_skeleton_command
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command

_FAST_PATH_INTENTS = frozenset(
    {
        AiIntentKind.NAVIGATE_SECTION,
        AiIntentKind.SHOW_OVERDUE,
        AiIntentKind.QUERY_MISSING_PPE,
        AiIntentKind.QUERY_DAILY_FOCUS,
        AiIntentKind.QUERY_OVERDUE_SUMMARY,
        AiIntentKind.QUERY_SECTION_PROBLEMS,
        AiIntentKind.OPEN_EMPLOYEE_CARD,
        AiIntentKind.QUERY_MODULE_STATUS,
        AiIntentKind.QUERY_EMPLOYEES_FILTER,
        AiIntentKind.QUERY_WORK_PERMIT_LIST,
        AiIntentKind.QUERY_WORK_PERMIT_READINESS,
        AiIntentKind.QUERY_PORT_R_GAPS,
        AiIntentKind.EXPLAIN_HELP,
        AiIntentKind.GENERATE_REPORT_TEXT,
        AiIntentKind.QUERY_EMPLOYEE_READINESS,
    }
)


def try_match_high_confidence_fast_path_command(command_text: str) -> AiCommandDraft | None:
    """Повертає draft лише для однозначних nav/read команд без LLM.
    Returns a draft only for unambiguous nav/read commands without LLM.
    """

    normalized = command_text.strip()
    if not normalized:
        return None

    routed = try_match_intent_skeleton_command(normalized)
    if routed is not None and routed.intent in _FAST_PATH_INTENTS:
        return routed

    routed = try_match_simple_ai_command(normalized)
    if routed is not None and routed.intent in _FAST_PATH_INTENTS:
        return routed

    list_query = extract_module_status_query_from_command(normalized)
    if list_query is not None:
        module_key, filter_key = list_query
        return AiCommandDraft(
            intent=AiIntentKind.QUERY_MODULE_STATUS,
            raw_command=normalized,
            source="fast_path",
            module_key=module_key,
            filter_key=filter_key,
            needs_confirmation=False,
        )

    return None
