from dataclasses import dataclass, replace
from pathlib import Path
import re

from osah.application.services.change_work_permit_participants import change_work_permit_participants
from osah.application.services.reissue_work_permit_record import reissue_work_permit_record
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


@dataclass(frozen=True, slots=True)
class WorkPermitParticipantChangeOutcome:
    """Результат зміни складу бригади наряду-допуску.
    Outcome of a work-permit brigade-composition change.
    """

    applied_record_id: int
    reissued: bool


def apply_work_permit_participant_change(
    database_path: Path,
    record_id: int,
    participants: tuple,
    reissue_reason_text: str = "Змінено більше 50% складу бригади.",
    *,
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> WorkPermitParticipantChangeOutcome:
    """Застосовує зміну складу бригади або перевипускає наряд при великій заміні.
    Applies a brigade change or reissues the permit when the replacement is too large.
    """

    ensure_write_access(access_role, "apply_work_permit_participant_change")
    try:
        change_work_permit_participants(database_path, record_id, participants, access_role=access_role)
    except ValueError as error:
        if "50%" not in str(error):
            raise
    else:
        return WorkPermitParticipantChangeOutcome(applied_record_id=record_id, reissued=False)

    source_record = _load_work_permit_record(database_path, record_id)
    if source_record.status == WorkPermitStatus.EXPIRED:
        raise ValueError(
            "Строк дії наряду вже сплив. Спочатку закрийте його або створіть новий наряд з актуальними строками."
        )
    reissued_record = _build_reissued_record(
        source_record,
        participants,
        _generate_reissued_permit_number(database_path, source_record.permit_number),
    )
    new_record_id = reissue_work_permit_record(
        database_path,
        record_id,
        reissued_record,
        reissue_reason_text,
        access_role=access_role,
    )
    return WorkPermitParticipantChangeOutcome(applied_record_id=new_record_id, reissued=True)


def _load_work_permit_record(database_path: Path, record_id: int) -> WorkPermitRecord:
    connection = create_database_connection(database_path)
    try:
        record = next(
            (item for item in list_work_permit_records(connection) if int(item.record_id or 0) == int(record_id)),
            None,
        )
    finally:
        connection.close()

    if record is None:
        raise ValueError("Обраний наряд-допуск не знайдено.")
    return record


def _build_reissued_record(
    source_record: WorkPermitRecord,
    participants: tuple,
    permit_number: str,
) -> WorkPermitRecord:
    return replace(
        source_record,
        record_id=None,
        permit_number=permit_number,
        closed_at=None,
        canceled_at=None,
        cancel_reason_text="",
        daily_checks=(),
        reissued_from_record_id=None,
        reissued_to_record_id=None,
        reissue_reason_text="",
        participants=participants,
        status=WorkPermitStatus.ACTIVE,
    )


def _generate_reissued_permit_number(database_path: Path, source_permit_number: str) -> str:
    connection = create_database_connection(database_path)
    try:
        existing_numbers = {
            item.permit_number.strip()
            for item in list_work_permit_records(connection)
            if item.permit_number.strip()
        }
    finally:
        connection.close()

    root_number, next_index = _split_reissued_permit_number(source_permit_number)
    while True:
        candidate = f"{root_number}-R{next_index}"
        if candidate not in existing_numbers:
            return candidate
        next_index += 1


def _split_reissued_permit_number(source_permit_number: str) -> tuple[str, int]:
    match = re.fullmatch(r"(?P<root>.+)-R(?P<index>\d+)", source_permit_number.strip())
    if match is None:
        return source_permit_number.strip(), 1
    return match.group("root"), int(match.group("index")) + 1
