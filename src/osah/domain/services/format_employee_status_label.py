from osah.domain.entities.employee_status_level import EmployeeStatusLevel


# ###### ФОРМАТУВАННЯ СТАТУСУ ПРАЦІВНИКА / FORMAT EMPLOYEE STATUS ######
def format_employee_status_label(status_level: EmployeeStatusLevel) -> str:
    """Повертає короткий україномовний підпис агрегованого статусу працівника.
    Returns a short Ukrainian label for the aggregated employee status.
    """

    labels = {
        EmployeeStatusLevel.NORMAL: "Норма",
        EmployeeStatusLevel.WARNING: "Увага",
        EmployeeStatusLevel.CRITICAL: "Критично",
        EmployeeStatusLevel.RESTRICTED: "Обмежено",
        EmployeeStatusLevel.ARCHIVED: "Архів",
    }
    return labels[status_level]
