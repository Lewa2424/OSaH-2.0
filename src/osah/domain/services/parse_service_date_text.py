from datetime import date

from osah.domain.services.parse_ui_date_text import parse_ui_date_text


def parse_service_date_text(date_text: str) -> date:
    """Парсить дату з UI-формату або ISO-рядка для сервісного шару.
    Parses a date from UI format or ISO string for the service layer.
    """

    normalized = date_text.strip()
    try:
        return parse_ui_date_text(normalized)
    except ValueError:
        try:
            return date.fromisoformat(normalized)
        except ValueError as error:
            raise ValueError("Введите дату в формате ДД.ММ.ГГГГ. Допустимо: 1.1.26 или 01,01,2026.") from error
