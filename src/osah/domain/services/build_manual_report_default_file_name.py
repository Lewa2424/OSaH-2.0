from datetime import datetime


# ###### ІМ'Я ФАЙЛУ РУЧНОГО ЩОДЕННОГО ЗВІТУ / MANUAL DAILY REPORT DEFAULT FILE NAME ######
def build_manual_report_default_file_name(current_moment: datetime | None = None) -> str:
    """Повертає зрозуміле стандартне ім'я файлу для ручного збереження щоденного звіту.
    Returns a clear default file name for manually saving the daily report.
    """

    moment = current_moment or datetime.now()
    return f"ClearWork_щоденний_звіт_{moment.strftime('%Y-%m-%d_%H-%M')}.txt"
