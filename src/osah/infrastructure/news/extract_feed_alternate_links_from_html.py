from html.parser import HTMLParser
from urllib.parse import urljoin


class _FeedAlternateLinksParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self._base_url = base_url
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "link":
            return
        attributes = {key.lower(): (value or "") for key, value in attrs}
        rel_value = attributes.get("rel", "").lower()
        type_value = attributes.get("type", "").lower()
        href_value = attributes.get("href", "").strip()
        if "alternate" not in rel_value or not href_value:
            return
        if type_value not in {
            "application/rss+xml",
            "application/atom+xml",
            "application/xml",
            "text/xml",
        }:
            return
        self.links.append(urljoin(self._base_url, href_value))


# ###### ВИТЯГ RSS/ATOM ПОСИЛАНЬ З HTML / ИЗВЛЕЧЕНИЕ RSS/ATOM ССЫЛОК ИЗ HTML ######
def extract_feed_alternate_links_from_html(page_url: str, html_text: str) -> tuple[str, ...]:
    """Повертає RSS/Atom-посилання, знайдені в HTML сторінки.
    Возвращает RSS/Atom-ссылки, найденные в HTML страницы.
    """

    parser = _FeedAlternateLinksParser(page_url)
    parser.feed(html_text)
    return tuple(dict.fromkeys(parser.links))
