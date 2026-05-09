from urllib.parse import urlparse


# ###### ПОБУДОВА НАЗВИ ДЖЕРЕЛА З URL / ПОСТРОЕНИЕ НАЗВАНИЯ ИСТОЧНИКА ИЗ URL ######
def build_news_source_name_from_url(source_url: str) -> str:
    """Повертає коротку назву джерела на основі домену URL.
    Возвращает краткое название источника на основе домена URL.
    """

    parsed_url = urlparse(source_url.strip())
    host_name = parsed_url.netloc.lower().removeprefix("www.")
    if host_name:
        return host_name
    return source_url.strip()
