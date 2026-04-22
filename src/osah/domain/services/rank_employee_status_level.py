from osah.domain.entities.employee_status_level import EmployeeStatusLevel


# ###### РАНГ СТАТУСУ ПРАЦІВНИКА / EMPLOYEE STATUS RANK ######
def rank_employee_status_level(status_level: EmployeeStatusLevel) -> int:
    """Повертає вагу статусу для вибору найважчої проблеми.
    Returns status weight for selecting the most severe problem.
    """

    ranks = {
        EmployeeStatusLevel.NORMAL: 0,
        EmployeeStatusLevel.WARNING: 1,
        EmployeeStatusLevel.RESTRICTED: 2,
        EmployeeStatusLevel.CRITICAL: 3,
        EmployeeStatusLevel.ARCHIVED: -1,
    }
    return ranks[status_level]
