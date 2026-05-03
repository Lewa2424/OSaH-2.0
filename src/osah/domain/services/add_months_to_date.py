from calendar import monthrange
from datetime import date


# ###### ДОБАВЛЕНИЕ МЕСЯЦЕВ К ДАТЕ / ADD MONTHS TO DATE ######
def add_months_to_date(source_date: date, month_total: int) -> date:
    """Возвращает дату, сдвинутую на заданное количество календарных месяцев.
    Returns a date shifted by the given number of calendar months.
    """

    target_month_index = source_date.month - 1 + month_total
    target_year = source_date.year + target_month_index // 12
    target_month = target_month_index % 12 + 1
    target_day = min(source_date.day, monthrange(target_year, target_month)[1])
    return date(target_year, target_month, target_day)
