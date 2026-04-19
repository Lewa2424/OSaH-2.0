from datetime import datetime


# ###### ПОБУДОВА ТЕМИ ЩОДЕННОГО ЗВІТУ / ПОСТРОЕНИЕ ТЕМЫ ЕЖЕДНЕВНОГО ОТЧЁТА ######
def build_daily_report_subject(created_at: datetime) -> str:
    """Повертає тему щоденного управлінського звіту.
    Возвращает тему ежедневного управленческого отчёта.
    """

    return f"Щоденний звіт з ОП за {created_at.strftime('%Y-%m-%d')}"
