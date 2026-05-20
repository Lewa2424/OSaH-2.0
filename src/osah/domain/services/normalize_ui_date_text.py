from osah.domain.services.parse_ui_date_text import parse_ui_date_text


# ###### НОРМАЛИЗАЦИЯ ДАТЫ ИЗ UI / NORMALIZE UI DATE TEXT ######
def normalize_ui_date_text(date_text: str) -> str:
    """Возвращает пользовательскую дату в каноническом UI-виде.
    Returns canonical UI representation for a user-entered date.
    """

    return parse_ui_date_text(date_text).strftime("%d.%m.%Y")
