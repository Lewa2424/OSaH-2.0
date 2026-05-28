from datetime import datetime

from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text


def parse_service_datetime_text(datetime_text: str) -> datetime:
    """Парсить дату-час із UI-формату або ISO-рядка для сервісного шару.
    Parses datetime from UI format or ISO string for the service layer.
    """

    normalized = datetime_text.strip()
    try:
        return parse_ui_datetime_text(normalized)
    except ValueError:
        try:
            return datetime.fromisoformat(normalized)
        except ValueError as error:
            raise ValueError("Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ. Допустимо: 1.1.26 8:00.") from error
