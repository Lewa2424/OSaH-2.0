from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.archive_entry import ArchiveEntry
from osah.domain.entities.archive_entry_type import ArchiveEntryType
from osah.domain.entities.archive_workspace import ArchiveWorkspace
from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ АРХІВУ / LOAD ARCHIVE WORKSPACE ######
def load_archive_workspace(database_path: Path) -> ArchiveWorkspace:
    """Builds archive registry from archived employees and historical permits."""

    employee_entries = tuple(
        ArchiveEntry(
            entry_key=f"employee:{employee.personnel_number}",
            entry_type=ArchiveEntryType.EMPLOYEE,
            title=employee.full_name,
            subtitle=f"{employee.position_name} • {employee.department_name}",
            status_label=employee.employment_status,
            archived_at_text="n/a",
            reason_text="Статус працівника позначено як архівний.",
            can_reactivate=True,
        )
        for employee in load_employee_registry(database_path)
        if employee.employment_status.lower() in {"archived", "inactive", "dismissed"}
    )
    permit_entries = tuple(
        ArchiveEntry(
            entry_key=f"work_permit:{record.record_id}",
            entry_type=ArchiveEntryType.WORK_PERMIT,
            title=f"Наряд {record.permit_number}",
            subtitle=f"{record.work_kind} • {record.work_location}",
            status_label=record.status.value,
            archived_at_text=record.closed_at or record.canceled_at or "n/a",
            reason_text=record.cancel_reason_text or record.note_text or "Історичний наряд-допуск.",
            can_reactivate=False,
        )
        for record in load_work_permit_registry(database_path)
        if record.status in {WorkPermitStatus.CLOSED, WorkPermitStatus.CANCELED}
    )
    return ArchiveWorkspace(entries=employee_entries + permit_entries)
