from datetime import datetime
from pathlib import Path

from osah.application.services.load_manual_report_settings import load_manual_report_settings


# ###### ПЕРЕВІРКА НЕОБХІДНОСТІ НАГАДУВАННЯ ПРО ЗВІТ / CHECK MANUAL REPORT PROMPT ######
def should_prompt_manual_report(database_path: Path, current_moment: datetime | None = None) -> bool:
    """Повертає True, якщо настав час нагадати користувачу сформувати щоденний звіт.
    Returns True when it is time to remind the user to generate the daily report.
    """

    moment = current_moment or datetime.now()
    settings = load_manual_report_settings(database_path)
    if not settings.manual_reminder_enabled:
        return False

    today_text = moment.strftime("%Y-%m-%d")
    if settings.last_generated_date == today_text:
        return False
    if settings.last_skipped_date == today_text:
        return False

    if settings.next_prompt_at.strip():
        try:
            if moment < datetime.fromisoformat(settings.next_prompt_at.strip()):
                return False
        except ValueError:
            pass

    configured_hour, configured_minute = _parse_report_time(settings.manual_reminder_time)
    configured_moment = moment.replace(hour=configured_hour, minute=configured_minute, second=0, microsecond=0)
    return moment >= configured_moment


def _parse_report_time(configured_time_text: str) -> tuple[int, int]:
    """Повертає години та хвилини з рядка часу або безпечне значення за замовчуванням.
    Returns hour and minute from a time string or a safe default value.
    """

    try:
        hour_text, minute_text = configured_time_text.strip().split(":", maxsplit=1)
        hour_value = max(0, min(23, int(hour_text)))
        minute_value = max(0, min(59, int(minute_text)))
        return hour_value, minute_value
    except (AttributeError, TypeError, ValueError):
        return 8, 0
