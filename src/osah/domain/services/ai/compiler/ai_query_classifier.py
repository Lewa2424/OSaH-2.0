from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.extract_bulk_audience_from_command import has_implicit_bulk_audience_marker
from osah.domain.services.ai.extract_module_status_query_from_command import extract_module_status_query_from_command
from osah.domain.services.ai.matches_employee_problems_query import matches_employee_problems_query
from osah.domain.services.ai.matches_module_status_list_query import matches_module_status_list_query
from osah.domain.services.ai.detect_ai_command_track import matches_section_problems_query


def classify_list_query_intent(raw_command: str) -> AiIntentKind | None:
    """Класифікує list-query без персональної цілі.
    Classifies list queries without a personal target.
    """

    if matches_module_status_list_query(raw_command):
        return AiIntentKind.QUERY_MODULE_STATUS
    if matches_section_problems_query(raw_command):
        return AiIntentKind.QUERY_SECTION_PROBLEMS
    return None


def is_personal_read_query(raw_command: str, draft: AiCommandDraft) -> bool:
    """Перевіряє персональний read-запит (проблеми/готовність працівника).
    Checks for a personal employee readiness query.
    """

    if matches_employee_problems_query(raw_command):
        return bool(draft.employee_query or draft.personnel_number)
    return False


def is_audience_write_command(raw_command: str) -> bool:
    """Перевіряє write-команду з груповою аудиторією.
    Checks for a write command with group audience.
    """

    return has_implicit_bulk_audience_marker(raw_command)
