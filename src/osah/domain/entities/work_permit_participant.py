from dataclasses import dataclass

from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole


@dataclass(slots=True)
class WorkPermitParticipant:
    """Учасник наряду-допуску.
    Участник наряда-допуска.
    """

    employee_personnel_number: str
    employee_full_name: str
    participant_role: WorkPermitParticipantRole
