from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### ПОБУДОВА ЗВЕДЕННЯ НАРЯДІВ-ДОПУСКІВ / ПОСТРОЕНИЕ СВОДКИ НАРЯДОВ-ДОПУСКОВ ######
def build_work_permit_summary(work_permit_records: tuple[WorkPermitRecord, ...]) -> tuple[str, ...]:
    """Повертає короткі рядки для картки працівника по модулю нарядів-допусків.
    Возвращает короткие строки для карточки сотрудника по модулю нарядов-допусков.
    """

    if not work_permit_records:
        return ("Активних нарядів-допусків поки немає.",)

    sorted_records = sorted(work_permit_records, key=lambda work_permit_record: work_permit_record.ends_at)
    return tuple(
        f"{work_permit_record.permit_number} | {_format_work_permit_status(work_permit_record.status)} | {work_permit_record.ends_at}"
        for work_permit_record in sorted_records[:3]
    )


# ###### ФОРМАТУВАННЯ СТАТУСУ НАРЯДУ / ФОРМАТИРОВАНИЕ СТАТУСА НАРЯДА ######
def _format_work_permit_status(work_permit_status: WorkPermitStatus) -> str:
    """Повертає коротку локалізовану мітку статусу наряду-допуску.
    Возвращает краткую локализованную метку статуса наряда-допуска.
    """

    if work_permit_status == WorkPermitStatus.ACTIVE:
        return "Активний"
    if work_permit_status == WorkPermitStatus.WARNING:
        return "Увага"
    if work_permit_status == WorkPermitStatus.EXPIRED:
        return "Прострочено"
    return "Закрито"
