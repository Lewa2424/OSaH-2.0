import re
from datetime import date

from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text

_HIGH_RISK_PATTERN = re.compile(
    r"(?:опасн\w*|небезпеч\w*|підвищен\w*\s+небезп\w*|high[\s_-]?risk|high_risk)",
    re.IGNORECASE,
)
_REGULAR_RISK_PATTERN = re.compile(
    r"(?:обычн\w*|звичайн\w*|regular|інших?\s+робіт|других?\s+работ)",
    re.IGNORECASE,
)
_DURATION_MONTHS_PATTERN = re.compile(
    r"(?:на\s+)?(\d+)\s*(?:міс(?:яц(?:ів|ев?)?)?|мес(?:яц(?:ев?)?)?|month)",
    re.IGNORECASE,
)
_DURATION_YEARS_PATTERN = re.compile(
    r"(?:на\s+)?(\d+)\s*(?:рік|рок(?:ів|и)?|year)",
    re.IGNORECASE,
)


def normalize_work_risk_category_from_text(raw_value: str | None) -> str | None:
    """Нормалізує категорію робіт із тексту користувача.
    Normalizes work risk category from user text.
    """

    if not raw_value or not raw_value.strip():
        return None
    text = raw_value.strip()
    if _HIGH_RISK_PATTERN.search(text):
        return "high_risk"
    if _REGULAR_RISK_PATTERN.search(text):
        return "regular"
    lowered = text.lower().replace(" ", "_")
    if lowered in {"high_risk", "regular", "not_applicable"}:
        return lowered
    return None


def extract_work_risk_category_from_command(raw_command: str) -> str | None:
    """Витягує категорію робіт із повної команди.
    Extracts work risk category from full command text.
    """

    category_match = re.search(
        r"(?:категор(?:ія|ия)|category)\s*[-:]\s*(.+?)(?:$|[,.])",
        raw_command,
        re.IGNORECASE,
    )
    if category_match:
        return normalize_work_risk_category_from_text(category_match.group(1))
    return normalize_work_risk_category_from_text(raw_command)


def parse_relative_period_from_command(
    raw_command: str,
    *,
    reference_date: date | None = None,
) -> tuple[str | None, bool]:
    """Повертає (дата_строк, use_manual_next_control) для «на N місяців».
    Returns (date_string, use_manual_next_control) for relative period phrases.
    """

    today = reference_date or date.today()
    month_match = _DURATION_MONTHS_PATTERN.search(raw_command)
    if month_match:
        months = max(1, int(month_match.group(1)))
        target = _add_months(today, months)
        return normalize_ai_issue_date_text(target.strftime("%d.%m.%Y")), True

    year_match = _DURATION_YEARS_PATTERN.search(raw_command)
    if year_match:
        years = max(1, int(year_match.group(1)))
        target = _add_years(today, years)
        return normalize_ai_issue_date_text(target.strftime("%d.%m.%Y")), True

    return None, False


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, _days_in_month(year, month))
    return date(year, month, day)


def _add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + years)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - date(year, month, 1)).days
