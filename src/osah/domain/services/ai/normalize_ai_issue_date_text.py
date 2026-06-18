from datetime import date

from osah.domain.services.ai.ai_relative_date_markers import mentions_current_date

_RELATIVE_DATE_ALIASES: dict[str, str] = {
    "today": "today",
    "сьогодні": "today",
    "сегодня": "today",
    "tomorrow": "tomorrow",
    "завтра": "tomorrow",
}


def normalize_ai_issue_date_text(issue_date: str | None) -> str:
    """Нормалізує відносну дату AI-команди до UI-формату.
    Normalizes a relative AI issue date into UI date text.
    """

    if issue_date is None:
        return _format_ui_date(date.today())

    normalized = issue_date.strip().lower()
    if not normalized:
        return _format_ui_date(date.today())

    if mentions_current_date(normalized):
        return _format_ui_date(date.today())

    alias = _RELATIVE_DATE_ALIASES.get(normalized)
    if alias == "today":
        return _format_ui_date(date.today())
    if alias == "tomorrow":
        return _format_ui_date(date.fromordinal(date.today().toordinal() + 1))

    return issue_date.strip()


def _format_ui_date(value: date) -> str:
    return value.strftime("%d.%m.%Y")
