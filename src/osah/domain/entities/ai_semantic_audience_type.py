from enum import StrEnum


class AiSemanticAudienceType(StrEnum):
    """Тип аудитории, которую затрагивает AI-команда.
    Type of audience affected by an AI command.
    """

    NONE = "none"
    EMPLOYEE = "employee"
    EMPLOYEE_LIST = "employee_list"
    DEPARTMENT = "department"
    POSITION = "position"
    WORK_PERMIT_PARTICIPANTS = "work_permit_participants"
    EMPLOYEE_FILTER = "employee_filter"
