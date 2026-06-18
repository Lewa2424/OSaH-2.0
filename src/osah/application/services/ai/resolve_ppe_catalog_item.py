from pathlib import Path

from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates


def resolve_ppe_catalog_item(database_path: Path, item_name: str) -> str | None:
    """Підбирає найближчу назву ЗІЗ із наявних записів.
    Resolves the closest PPE name from existing records.
    """

    candidates = search_ppe_catalog_candidates(database_path, item_name, limit=1)
    if candidates:
        return candidates[0]
    normalized = item_name.strip()
    return normalized or None
