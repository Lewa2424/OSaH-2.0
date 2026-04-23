from dataclasses import dataclass

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus


@dataclass(slots=True)
class WorkPermitWorkspaceRow:
    """Рядок Qt-реєстру нарядів-допусків з причиною статусу.
    Qt work permit registry row with status reason.
    """

    record: WorkPermitRecord
    record_id: int | None
    permit_number: str
    work_kind: str
    work_location: str
    department_name: str
    site_name: str
    starts_at: str
    ends_at: str
    responsible_person: str
    issuer_person: str
    participant_count: int
    participant_names: str
    employee_numbers: tuple[str, ...]
    status: WorkPermitStatus
    status_label: str
    status_reason: str
    has_conflicts: bool
    conflict_reasons: tuple[str, ...]
