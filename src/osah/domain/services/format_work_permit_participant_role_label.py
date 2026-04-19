from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole


# ###### ФОРМАТУВАННЯ РОЛІ УЧАСНИКА НАРЯДУ / ФОРМАТИРОВАНИЕ РОЛИ УЧАСТНИКА НАРЯДА ######
def format_work_permit_participant_role_label(participant_role: WorkPermitParticipantRole) -> str:
    """Повертає локалізовану назву ролі учасника наряду-допуску.
    Возвращает локализованное название роли участника наряда-допуска.
    """

    if participant_role == WorkPermitParticipantRole.EXECUTOR:
        return "Виконавець"
    if participant_role == WorkPermitParticipantRole.TEAM_MEMBER:
        return "Член бригади"
    return "Спостерігач"
