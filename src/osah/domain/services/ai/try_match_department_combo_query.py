from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.extract_department_module_status_query import extract_department_module_status_query


def try_match_department_combo_query(command_text: str) -> AiCommandDraft | None:
    """Повертає one-shot запит «підрозділ + проблеми в інструктажах».
    Returns a one-shot department plus training problems query draft.
    """

    combo = extract_department_module_status_query(command_text)
    if combo is None:
        return None

    department_query, module_key, filter_key = combo
    return AiCommandDraft(
        intent=AiIntentKind.QUERY_MODULE_STATUS,
        raw_command=command_text.strip(),
        source="intent_skeleton",
        department_query=department_query,
        module_key=module_key,
        filter_key=filter_key,
        needs_confirmation=False,
    )
