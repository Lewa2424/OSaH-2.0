from dataclasses import dataclass

from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus


@dataclass(slots=True)
class EmployeeImportDraft:
    """Чернетка імпорту працівника до підтвердження.
    Черновик импорта сотрудника до подтверждения.
    """

    draft_id: int | None
    batch_id: int
    source_row_number: int
    personnel_number: str
    full_name: str
    position_name: str
    department_name: str
    employment_status: str
    resolution_status: EmployeeImportDraftStatus
    issue_text: str
