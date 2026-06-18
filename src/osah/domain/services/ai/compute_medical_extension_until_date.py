import re
from datetime import date

from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text

_DURATION_YEARS_PATTERN = re.compile(
    r"(?:на\s+)?(?:(\d+)\s*)?(?:год|рік|year|рок(?:ів|и)?)",
    re.IGNORECASE,
)
_DURATION_MONTHS_PATTERN = re.compile(
    r"на\s+(\d+)\s*(?:міс|мес|month)",
    re.IGNORECASE,
)


def compute_medical_extension_until_date(raw_command: str, *, today: date | None = None) -> str:
    """Обчислює нову дату закінчення меддопуску за текстом команди.
    Computes a new medical permit end date from command text.
    """

    reference_date = today or date.today()
    month_match = _DURATION_MONTHS_PATTERN.search(raw_command)
    if month_match is not None:
        months = max(1, int(month_match.group(1)))
        return normalize_ai_issue_date_text(_add_months(reference_date, months))

    year_match = _DURATION_YEARS_PATTERN.search(raw_command)
    years = 1
    if year_match is not None and year_match.group(1):
        years = max(1, int(year_match.group(1)))
    return normalize_ai_issue_date_text(_add_years(reference_date, years))


def _add_years(value: date, years: int) -> str:
    try:
        return value.replace(year=value.year + years).strftime("%d.%m.%Y")
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + years).strftime("%d.%m.%Y")


def _add_months(value: date, months: int) -> str:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, _days_in_month(year, month))
    return date(year, month, day).strftime("%d.%m.%Y")


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    current_month = date(year, month, 1)
    return (next_month - current_month).days
