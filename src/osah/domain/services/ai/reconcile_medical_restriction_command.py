import re
from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.should_preserve_trusted_semantic_slot import should_preserve_trusted_slot

_RESTRICTION_KEYWORD_PATTERN = re.compile(
    r"(?:ограничен\w*|обмежен\w*)",
    re.IGNORECASE,
)
_RESTRICTION_NOTE_PATTERN = re.compile(
    r"(?:ограничен\w*|обмежен\w*)\s*(?::\s*)?(?:по\s+)?(.+?)(?=\.|$)",
    re.IGNORECASE,
)


def reconcile_medical_restriction_command(draft: AiCommandDraft) -> AiCommandDraft:
    """Перетворює фразу з медобмеженням на UPDATE_MEDICAL_RECORD.
    Converts a medical restriction phrase into UPDATE_MEDICAL_RECORD.
    """

    raw_command = draft.raw_command.strip()
    if not raw_command or not _RESTRICTION_KEYWORD_PATTERN.search(raw_command):
        return draft

    trusted_employee = (draft.employee_query or "").strip()
    if trusted_employee and _RESTRICTION_KEYWORD_PATTERN.search(trusted_employee):
        employee_query = extract_employee_query_from_command(raw_command)
    elif should_preserve_trusted_slot(draft, "employee_query"):
        employee_query = draft.employee_query
    else:
        employee_query = draft.employee_query or extract_employee_query_from_command(raw_command)

    restriction_note = (draft.restriction_note or "").strip() or _extract_restriction_note(raw_command)
    return replace(
        draft,
        intent=AiIntentKind.UPDATE_MEDICAL_RECORD,
        module_key="medical",
        employee_query=employee_query,
        restriction_note=restriction_note,
        bulk_audience_spec=None,
        needs_confirmation=True,
    )


def _extract_restriction_note(raw_command: str) -> str | None:
    match = _RESTRICTION_NOTE_PATTERN.search(raw_command)
    if match is None:
        return None
    note = match.group(1).strip(" ,.;:")
    return note or None
