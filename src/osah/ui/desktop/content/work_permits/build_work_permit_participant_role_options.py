from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label


# ###### ПОБУДОВА ОПЦІЙ РОЛЕЙ НАРЯДУ / ПОСТРОЕНИЕ ОПЦИЙ РОЛЕЙ НАРЯДА ######
def build_work_permit_participant_role_options() -> tuple[str, ...]:
    """Повертає локалізовані підписи ролей учасника наряду-допуску.
    Возвращает локализованные подписи ролей участника наряда-допуска.
    """

    return tuple(
        format_work_permit_participant_role_label(participant_role)
        for participant_role in WorkPermitParticipantRole
    )
