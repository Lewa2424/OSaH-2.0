from pathlib import Path

from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus


def find_ppe_record_for_issuance(
    database_path: Path,
    personnel_number: str,
    ppe_item_query: str,
) -> PpeRecord | None:
    """Знаходить існуючий невиданий запис ЗІЗ для видачі замість дубля.
    Finds an existing unissued PPE record to issue instead of creating a duplicate.
    """

    normalized_number = personnel_number.strip()
    if not normalized_number:
        return None

    catalog_names = {name.lower() for name in search_ppe_catalog_candidates(database_path, ppe_item_query)}
    if not catalog_names:
        catalog_names = {ppe_item_query.strip().lower()}

    matches = [
        record
        for record in load_ppe_registry(database_path)
        if record.employee_personnel_number == normalized_number
        and record.ppe_name.strip().lower() in catalog_names
        and _is_open_for_issuance(record)
    ]
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    not_issued = [record for record in matches if record.status == PpeStatus.NOT_ISSUED]
    if len(not_issued) == 1:
        return not_issued[0]
    return None


def _is_open_for_issuance(record: PpeRecord) -> bool:
    if record.status == PpeStatus.NOT_ISSUED:
        return True
    if not record.is_issued:
        return True
    return record.provision_status == PpeProvisionStatus.REQUIRED_NOT_ISSUED
