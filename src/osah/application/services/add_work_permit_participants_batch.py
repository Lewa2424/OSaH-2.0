from pathlib import Path

from osah.application.services.change_work_permit_participants import change_work_permit_participants
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole


def add_work_permit_participants_batch(
    database_path: Path,
    permit_number: str,
    employee_personnel_numbers: tuple[str, ...],
    participant_role: str = "worker",
    *,
    access_role: AccessRole,
) -> int:
    """Додає учасників до наряду одним викликом.
    Adds participants to a work permit in one operation.
    """

    ensure_write_access(access_role, "add_work_permit_participants_batch")
    normalized_permit_number = permit_number.strip().lstrip("№")
    normalized_numbers = tuple(number.strip() for number in employee_personnel_numbers if number.strip())
    if not normalized_permit_number:
        raise ValueError("Потрібен номер наряду.")
    if not normalized_numbers:
        raise ValueError("Потрібно вказати учасників.")

    permit_record = next(
        (
            permit
            for permit in load_work_permit_registry(database_path)
            if permit.permit_number.strip().lstrip("№") == normalized_permit_number
        ),
        None,
    )
    if permit_record is None or permit_record.record_id is None:
        raise ValueError("Наряд-допуск не знайдено.")

    employees_by_number = {
        employee.personnel_number: employee for employee in load_employee_registry(database_path)
    }
    role = WorkPermitParticipantRole(participant_role.strip() or "worker")
    existing_numbers = {participant.employee_personnel_number for participant in permit_record.participants}
    new_participants = list(permit_record.participants)
    added_count = 0
    for personnel_number in normalized_numbers:
        if personnel_number in existing_numbers:
            continue
        employee = employees_by_number.get(personnel_number)
        full_name = employee.full_name if employee is not None else ""
        new_participants.append(
            WorkPermitParticipant(
                employee_personnel_number=personnel_number,
                employee_full_name=full_name,
                participant_role=role,
            )
        )
        added_count += 1

    if added_count == 0:
        return 0

    change_work_permit_participants(
        database_path,
        permit_record.record_id,
        tuple(new_participants),
        access_role=access_role,
    )
    return added_count
