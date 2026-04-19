from osah.domain.entities.news_item import NewsItem


# ###### ПОБУДОВА ОПЦІЙ ВИБОРУ НОВИННОГО МАТЕРІАЛУ / ПОСТРОЕНИЕ ОПЦИЙ ВЫБОРА НОВОСТНОГО МАТЕРИАЛА ######
def build_news_item_options(news_items: tuple[NewsItem, ...]) -> tuple[str, ...]:
    """Повертає рядки вибору для непрочитаних матеріалів.
    Возвращает строки выбора для непрочитанных материалов.
    """

    return tuple(f"{news_item.item_id} | {news_item.source_name} | {news_item.title_text}" for news_item in news_items)
