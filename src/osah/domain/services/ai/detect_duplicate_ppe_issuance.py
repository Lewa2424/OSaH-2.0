from pathlib import Path

from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text


def detect_duplicate_ppe_issuance(
    database_path: Path,
    *,
    personnel_number: str,
    ppe_name: str,
    issue_date_text: str | None,
) -> bool:
    """Перевіряє, чи вже існує схожий запис видачі ЗІЗ.
    Checks whether a similar PPE issuance record already exists.
    """

    normalized_number = personnel_number.strip()
    normalized_name = ppe_name.strip().lower()
    normalized_issue_date = normalize_ai_issue_date_text(issue_date_text)
    if not normalized_number or not normalized_name:
        return False

    for record in load_ppe_registry(database_path):
        if record.employee_personnel_number != normalized_number:
            continue
        if record.ppe_name.strip().lower() != normalized_name:
            continue
        if record.issue_date == normalized_issue_date:
            return True
        if record.is_issued and record.status in {PpeStatus.CURRENT, PpeStatus.WARNING}:
            return True
    return False
