from dataclasses import dataclass

from osah.domain.entities.ppe_status import PpeStatus


@dataclass(slots=True)
class PpeWorkspaceRow:
    """Рядок Qt-реєстру ЗІЗ із причиною статусу.
    Qt PPE registry row with status reason.
    """

    record_id: int | None
    employee_personnel_number: str
    employee_full_name: str
    department_name: str
    site_name: str
    position_name: str
    ppe_name: str
    is_required: bool
    is_issued: bool
    issue_date: str
    replacement_date: str
    quantity: int
    status: PpeStatus
    status_label: str
    status_reason: str
    note_text: str
