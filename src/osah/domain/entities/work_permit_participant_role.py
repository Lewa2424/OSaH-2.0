from enum import StrEnum


class WorkPermitParticipantRole(StrEnum):
    """Ролі учасника наряду-допуску.
    Роли участника наряда-допуска.
    """

    EXECUTOR = "executor"
    TEAM_MEMBER = "team_member"
    OBSERVER = "observer"
