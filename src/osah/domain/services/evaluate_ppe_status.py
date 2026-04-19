from datetime import date

from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus


# ###### ОЦІНКА СТАТУСУ ЗІЗ / ОЦЕНКА СТАТУСА СИЗ ######
def evaluate_ppe_status(
    ppe_record: PpeRecord,
    today: date | None = None,
    warning_days: int = 7,
) -> PpeStatus:
    """Повертає статус запису ЗІЗ за правилами обов'язковості й строку заміни.
    Возвращает статус записи СИЗ по правилам обязательности и срока замены.
    """

    if ppe_record.is_required and not ppe_record.is_issued:
        return PpeStatus.NOT_ISSUED

    current_date = today or date.today()
    replacement_date = date.fromisoformat(ppe_record.replacement_date)
    remaining_days = (replacement_date - current_date).days
    if remaining_days < 0:
        return PpeStatus.EXPIRED
    if remaining_days <= warning_days:
        return PpeStatus.WARNING
    return PpeStatus.CURRENT
