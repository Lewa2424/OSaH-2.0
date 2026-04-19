from osah.domain.entities.news_source_kind import NewsSourceKind


# ###### ФОРМАТУВАННЯ ТИПУ ДЖЕРЕЛА НОВИН / ФОРМАТИРОВАНИЕ ТИПА ИСТОЧНИКА НОВОСТЕЙ ######
def format_news_source_kind_label(source_kind: NewsSourceKind) -> str:
    """Повертає локалізовану назву типу зовнішнього джерела.
    Возвращает локализованное название типа внешнего источника.
    """

    if source_kind == NewsSourceKind.NPA:
        return "НПА"
    return "Новини"
