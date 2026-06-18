from dataclasses import replace

from osah.application.services.ai.resolve_ai_entities import apply_selected_ppe_item_choice
from osah.domain.entities.ai_command_draft import AiCommandDraft


def apply_grounding_entity_choice(
    draft: AiCommandDraft,
    choice_id: str,
    *,
    choice_kind: str,
) -> AiCommandDraft:
    """Підставляє вибрану сутність після ambiguous DB-grounding.
    Applies the selected entity after ambiguous DB grounding.
    """

    canonical = choice_id.strip()
    if choice_kind == "department":
        replace_kwargs: dict[str, object] = {"department_query": canonical}
        if (draft.filter_key or "").strip().lower() == "department":
            replace_kwargs["employee_query"] = canonical
        else:
            replace_kwargs["employee_query"] = None
        return replace(draft, **replace_kwargs)

    if choice_kind == "position":
        return replace(draft, position_query=canonical)

    if choice_kind == "ppe_item":
        return apply_selected_ppe_item_choice(draft, 0, canonical)

    return draft
