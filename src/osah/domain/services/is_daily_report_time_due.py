from datetime import datetime

from osah.domain.entities.mail_settings import MailSettings


# ###### ПЕРЕВІРКА ЧАСУ ЩОДЕННОГО ЗВІТУ / DAILY REPORT TIME CHECK ######
def is_daily_report_time_due(mail_settings: MailSettings, current_moment: datetime) -> bool:
    """Перевіряє, чи настав налаштований час щоденного звіту.
    Checks whether the configured daily report time has been reached.
    """

    configured_time = mail_settings.daily_report_time.strip() or "08:00"
    try:
        configured_hour, configured_minute = _parse_time(configured_time)
    except ValueError:
        configured_hour, configured_minute = 8, 0

    current_minutes = current_moment.hour * 60 + current_moment.minute
    configured_minutes = configured_hour * 60 + configured_minute
    return current_minutes >= configured_minutes


# ###### РОЗБІР ЧАСУ / TIME PARSING ######
def _parse_time(time_text: str) -> tuple[int, int]:
    """Розбирає значення HH:MM для службового планування звіту.
    Parses HH:MM value for report scheduling.
    """

    hour_text, minute_text = time_text.split(":", maxsplit=1)
    hour = int(hour_text)
    minute = int(minute_text)
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("Daily report time must be in HH:MM range.")
    return hour, minute
