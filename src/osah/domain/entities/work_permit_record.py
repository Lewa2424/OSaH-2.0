from dataclasses import dataclass

from osah.domain.entities.work_permit_daily_check import WorkPermitDailyCheck
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
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
    daily_checks: tuple[WorkPermitDailyCheck, ...] = ()
    reissued_from_record_id: int | None = None
    reissued_to_record_id: int | None = None
    reissue_reason_text: str = ""
    base_ends_at: str = ""
    extension_count: int = 0
    extended_at: str | None = None
    extension_reason_text: str = ""
    target_training_status: WorkPermitTargetTrainingStatus = WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED
    target_training_date: str = ""
    target_training_conducted_by: str = ""
    target_training_note: str = ""
    basis_text: str = ""
    basis_note: str = ""
