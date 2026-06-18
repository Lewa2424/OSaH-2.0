from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.extract_module_status_query_from_command import extract_module_status_query_from_command


def reconcile_module_status_query(draft: AiCommandDraft) -> AiCommandDraft:
    """Переводить списковий запит за статусом модуля в QUERY_MODULE_STATUS.
    Reconciles a module status list query into QUERY_MODULE_STATUS.
    """

    extracted = extract_module_status_query_from_command(draft.raw_command)
    if extracted is None:
        return draft

    module_key, filter_key = extracted
    return replace(
        draft,
        intent=AiIntentKind.QUERY_MODULE_STATUS,
        module_key=module_key,
        filter_key=filter_key,
        employee_query=None,
        personnel_number=None,
        training_type=None,
    )
