import re
from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.compute_medical_extension_until_date import compute_medical_extension_until_date
from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command

_EXTEND_MEDICAL_PATTERN = re.compile(
    r"(?:продл|продовж|подовж|продлен|extend).{0,50}(?:мед|med|меддопуск|медогляд)",
    re.IGNORECASE,
)


def reconcile_medical_extension_command(draft: AiCommandDraft) -> AiCommandDraft:
    """Перетворює команду продовження меддопуску на update з новим строком.
    Converts a medical permit extension phrase into an update with a new end date.
    """

    raw_command = draft.raw_command.strip()
    if not raw_command:
        return draft

    lowered = raw_command.lower()
    if not _EXTEND_MEDICAL_PATTERN.search(raw_command) and not (
        any(token in lowered for token in ("продл", "продовж", "подовж", "extend"))
        and any(token in lowered for token in ("мед", "med", "меддопуск", "медогляд"))
    ):
        return draft

    employee_query = draft.employee_query or extract_employee_query_from_command(raw_command)
    return replace(
        draft,
        intent=AiIntentKind.UPDATE_MEDICAL_RECORD,
        module_key="medical",
        employee_query=employee_query,
        issue_date=None,
        valid_until_date=compute_medical_extension_until_date(raw_command),
        needs_confirmation=True,
    )
