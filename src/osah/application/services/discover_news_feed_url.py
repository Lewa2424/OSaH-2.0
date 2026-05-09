from urllib.parse import urljoin, urlparse

from osah.infrastructure.news.extract_feed_alternate_links_from_html import extract_feed_alternate_links_from_html
from osah.infrastructure.news.is_feed_xml_content import is_feed_xml_content
from osah.infrastructure.news.read_web_document_from_url import read_web_document_from_url


_COMMON_FEED_PATHS: tuple[str, ...] = (
    "/feed",
    "/feed/",
    "/rss",
    "/rss/",
    "/rss.xml",
    "/feed.xml",
    "/atom.xml",
)


# ###### ПОШУК RSS/ATOM ДЛЯ САЙТУ / ПОИСК RSS/ATOM ДЛЯ САЙТА ######
def discover_news_feed_url(
    source_url: str,
    document_reader=read_web_document_from_url,
) -> str:
    """Повертає feed URL для сайту або піднімає помилку, якщо RSS/Atom не знайдено.
    Возвращает feed URL для сайта или поднимает ошибку, если RSS/Atom не найдено.
    """

    normalized_source_url = source_url.strip()
    if not normalized_source_url.startswith(("http://", "https://")):
        raise ValueError("Посилання на сайт має починатися з http:// або https://.")

    content_type, document_text = document_reader(normalized_source_url)
    if "xml" in content_type.lower() and is_feed_xml_content(document_text):
        return normalized_source_url
    if is_feed_xml_content(document_text):
        return normalized_source_url

    for candidate_url in extract_feed_alternate_links_from_html(normalized_source_url, document_text):
        try:
            _, candidate_document = document_reader(candidate_url)
        except Exception:  # noqa: BLE001
            continue
        if is_feed_xml_content(candidate_document):
            return candidate_url

    parsed_url = urlparse(normalized_source_url)
    site_root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    for common_path in _COMMON_FEED_PATHS:
        candidate_url = urljoin(site_root_url, common_path)
        try:
            _, candidate_document = document_reader(candidate_url)
        except Exception:  # noqa: BLE001
            continue
        if is_feed_xml_content(candidate_document):
            return candidate_url

    raise ValueError(
        "Для цього сайту не знайдено RSS/Atom-стрічку. Спробуйте пряме посилання на RSS/Atom або оберіть джерело зі списку."
    )
