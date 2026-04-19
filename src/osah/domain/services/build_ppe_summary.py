from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus


# ###### ПОБУДОВА ЗВЕДЕННЯ ЗІЗ / ПОСТРОЕНИЕ СВОДКИ СИЗ ######
def build_ppe_summary(ppe_records: tuple[PpeRecord, ...]) -> tuple[str, ...]:
    """Повертає короткі рядки для картки працівника по модулю ЗІЗ.
    Возвращает короткие строки для карточки сотрудника по модулю СИЗ.
    """

    if not ppe_records:
        return ("Записів по ЗІЗ поки немає.",)

    sorted_records = sorted(ppe_records, key=lambda ppe_record: ppe_record.replacement_date)
    return tuple(
        f"{ppe_record.ppe_name} | {ppe_record.replacement_date} | {_format_ppe_status(ppe_record.status)}"
        for ppe_record in sorted_records[:3]
    )


# ###### ФОРМАТУВАННЯ СТАТУСУ ЗІЗ У ЗВЕДЕННІ / ФОРМАТИРОВАНИЕ СТАТУСА СИЗ В СВОДКЕ ######
def _format_ppe_status(ppe_status: PpeStatus) -> str:
    """Повертає коротку локалізовану мітку статусу ЗІЗ.
    Возвращает краткую локализованную метку статуса СИЗ.
    """

    if ppe_status == PpeStatus.CURRENT:
        return "Актуально"
    if ppe_status == PpeStatus.WARNING:
        return "Увага"
    if ppe_status == PpeStatus.EXPIRED:
        return "Прострочено"
    return "Не видано"
