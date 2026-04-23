from dataclasses import dataclass

from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_status import WorkPermitStatus


@dataclass(slots=True)
class WorkPermitRecord:
    """Запис наряду-допуску з учасниками та статусом.
    Запись наряда-допуска с участниками и статусом.
    """

    record_id: int | None
    permit_number: str
    work_kind: str
    work_location: str
    starts_at: str
    ends_at: str
    responsible_person: str
    issuer_person: str
    note_text: str
    closed_at: str | None
    participants: tuple[WorkPermitParticipant, ...]
    status: WorkPermitStatus
    canceled_at: str | None = None
    cancel_reason_text: str = ""
