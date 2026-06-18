from pathlib import Path

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.services.ai.detect_duplicate_ppe_issuance import detect_duplicate_ppe_issuance


def filter_personnel_numbers_for_ppe_conditions(
    database_path: Path,
    draft: AiCommandDraft,
    personnel_numbers: tuple[str, ...],
) -> tuple[str, ...]:
    """Фільтрує аудиторію bulk PPE за semantic conditions.
    Filters bulk PPE audience by semantic conditions.
    """

    if "skip_if_active_ppe_exists" not in draft.semantic_conditions:
        return personnel_numbers

    item_names = [item.name for item in draft.items if item.name.strip()]
    if not item_names and draft.ppe_item_query:
        item_names = [draft.ppe_item_query]
    if not item_names:
        return personnel_numbers

    filtered: list[str] = []
    for personnel_number in personnel_numbers:
        has_active_duplicate = any(
            detect_duplicate_ppe_issuance(
                database_path,
                personnel_number=personnel_number,
                ppe_name=item_name,
                issue_date_text=draft.issue_date,
            )
            for item_name in item_names
        )
        if not has_active_duplicate:
            filtered.append(personnel_number)
    return tuple(filtered)
