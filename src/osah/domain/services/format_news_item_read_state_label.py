from osah.domain.entities.news_item_read_state import NewsItemReadState


# ###### ФОРМАТУВАННЯ СТАНУ ПРОЧИТАННЯ НОВИНИ / ФОРМАТИРОВАНИЕ СОСТОЯНИЯ ПРОЧТЕНИЯ НОВОСТИ ######
def format_news_item_read_state_label(read_state: NewsItemReadState) -> str:
    """Повертає локалізовану назву стану прочитання.
    Возвращает локализованное название состояния прочтения.
    """

    if read_state == NewsItemReadState.READ:
        return "Прочитано"
    return "Нове"
