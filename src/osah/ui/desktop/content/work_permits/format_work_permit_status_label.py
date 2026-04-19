from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ НАРЯДУ / ФОРМАТИРОВАНИЕ СТАТУСА НАРЯДА ######
def format_work_permit_status_label(work_permit_status: WorkPermitStatus) -> str:
    """Повертає локалізовану мітку статусу наряду-допуску для UI.
    Возвращает локализованную метку статуса наряда-допуска для UI.
    """

    if work_permit_status == WorkPermitStatus.ACTIVE:
        return "Активний"
    if work_permit_status == WorkPermitStatus.WARNING:
        return "Увага"
    if work_permit_status == WorkPermitStatus.EXPIRED:
        return "Прострочено"
    return "Закрито"
