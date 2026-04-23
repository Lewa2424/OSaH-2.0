from datetime import datetime
from pathlib import Path

from osah.application.services.load_mail_settings import load_mail_settings
from osah.application.services.send_daily_report_email import send_daily_report_email
from osah.domain.services.is_daily_report_time_due import is_daily_report_time_due
from osah.domain.services.is_mail_settings_ready import is_mail_settings_ready


# ###### НАДСИЛАННЯ ЩОДЕННОГО ЗВІТУ ЯКЩО НАСТАВ СТРОК / ОТПРАВКА ЕЖЕДНЕВНОГО ОТЧЁТА ЕСЛИ НАСТУПИЛ СРОК ######
def send_daily_report_if_due(database_path: Path, current_moment: datetime | None = None) -> None:
    """Пробує відправити щоденний звіт, якщо увімкнено доставку і сьогодні його ще не надсилали.
    Пытается отправить ежедневный отчёт, если доставка включена и сегодня его ещё не отправляли.
    """

    reference_moment = current_moment or datetime.now()
    mail_settings = load_mail_settings(database_path)
    if not mail_settings.daily_report_enabled:
        return
    if not is_mail_settings_ready(mail_settings):
        return
    if not is_daily_report_time_due(mail_settings, reference_moment):
        return
    if mail_settings.last_sent_date == reference_moment.strftime("%Y-%m-%d"):
        return

    try:
        send_daily_report_email(database_path)
    except Exception:  # noqa: BLE001
        return
