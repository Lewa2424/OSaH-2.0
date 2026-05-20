from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text


# ###### НОРМАЛИЗАЦИЯ DATETIME ИЗ UI / NORMALIZE UI DATETIME TEXT ######
def normalize_ui_datetime_text(datetime_text: str) -> str:
    """Возвращает пользовательские дату и время в каноническом UI-виде.
    Returns canonical UI representation for user-entered date and time.
    """

    return parse_ui_datetime_text(datetime_text).strftime("%d.%m.%Y %H:%M")
