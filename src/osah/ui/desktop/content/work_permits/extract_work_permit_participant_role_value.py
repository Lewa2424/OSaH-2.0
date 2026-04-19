from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label


# ###### ВИДІЛЕННЯ ТЕХНІЧНОЇ РОЛІ НАРЯДУ / ВЫДЕЛЕНИЕ ТЕХНИЧЕСКОЙ РОЛИ НАРЯДА ######
def extract_work_permit_participant_role_value(participant_role_label: str) -> str:
    """Повертає технічне значення ролі учасника за локалізованим підписом.
    Возвращает техническое значение роли участника по локализованной подписи.
    """

    for participant_role in WorkPermitParticipantRole:
        if format_work_permit_participant_role_label(participant_role) == participant_role_label:
            return participant_role.value
    return ""
