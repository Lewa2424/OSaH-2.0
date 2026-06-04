from urllib.request import Request, urlopen

from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.infrastructure.http.read_http_response_bytes_with_limit import read_http_response_bytes_with_limit
from osah.infrastructure.news.parse_feed_xml_content import parse_feed_xml_content


# ###### ЗАВАНТАЖЕННЯ FEED-ЗАПИСІВ З URL / ЗАГРУЗКА FEED-ЗАПИСЕЙ С URL ######
def fetch_feed_entries_from_url(source_url: str) -> tuple[RssFeedEntry, ...]:
    """Завантажує RSS або Atom-канал з URL і повертає нормалізовані записи.
    Загружает RSS или Atom-канал с URL и возвращает нормализованные записи.
    """

    request = Request(source_url, headers={"User-Agent": "OSaH/2.0"})
    with urlopen(request, timeout=20) as response:
        xml_content_text = read_http_response_bytes_with_limit(response).decode("utf-8", errors="replace")
    return parse_feed_xml_content(xml_content_text)
