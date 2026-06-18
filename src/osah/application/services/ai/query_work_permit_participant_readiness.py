from dataclasses import dataclass
from pathlib import Path

from osah.application.services.ai.query_employee_readiness import query_employee_readiness
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.work_permit_status import WorkPermitStatus


@dataclass(slots=True, frozen=True)
class WorkPermitParticipantReadinessRow:
    """Готовність учасника наряду.
    Work permit participant readiness row.
    """

    employee_name: str
    personnel_number: str
    ready: bool
    message: str


@dataclass(slots=True, frozen=True)
class WorkPermitReadinessQueryResult:
    """Результат перевірки готовності учасників наряду.
    Result of work permit participant readiness check.
    """

    permit_number: str
    participants: tuple[WorkPermitParticipantReadinessRow, ...]


def query_work_permit_participant_readiness(
    database_path: Path,
    *,
    permit_number: str | None = None,
    permit_query: str | None = None,
) -> WorkPermitReadinessQueryResult | None:
    """Перевіряє готовність учасників наряду.
    Checks readiness of work permit participants.
    """

    resolved_number = _resolve_permit_number(database_path, permit_number, permit_query)
    if resolved_number is None:
        return None

    permit = next(
        (item for item in load_work_permit_registry(database_path) if item.permit_number == resolved_number),
        None,
    )
    if permit is None:
        return None

    participant_rows: list[WorkPermitParticipantReadinessRow] = []
    for participant in permit.participants:
        readiness = query_employee_readiness(database_path, personnel_number=participant.employee_personnel_number)
        if readiness is None:
            participant_rows.append(
                WorkPermitParticipantReadinessRow(
                    employee_name=participant.employee_full_name or participant.employee_personnel_number,
                    personnel_number=participant.employee_personnel_number,
                    ready=False,
                    message="Працівника не знайдено.",
                )
            )
            continue
        participant_rows.append(
            WorkPermitParticipantReadinessRow(
                employee_name=readiness.employee_name,
                personnel_number=readiness.personnel_number,
                ready=readiness.overall_ready,
                message=f"{readiness.training_message}; {readiness.medical_message}; {readiness.ppe_message}",
            )
        )

    return WorkPermitReadinessQueryResult(
        permit_number=permit.permit_number,
        participants=tuple(participant_rows),
    )


def _resolve_permit_number(
    database_path: Path,
    permit_number: str | None,
    permit_query: str | None,
) -> str | None:
    direct = (permit_number or permit_query or "").strip()
    if not direct:
        return None
    for record in load_work_permit_registry(database_path):
        if record.permit_number.strip() == direct:
            return record.permit_number
        if direct.lower() in record.permit_number.lower():
            return record.permit_number
    return direct
