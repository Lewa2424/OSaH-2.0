from xml.etree.ElementTree import Element

from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.infrastructure.news.extract_xml_child_text import extract_xml_child_text
from osah.infrastructure.news.normalize_feed_publication_text import normalize_feed_publication_text


# ###### РОЗБІР RSS-СТРІЧКИ / РАЗБОР RSS-ЛЕНТЫ ######
def parse_rss_feed_entries(root_element: Element) -> tuple[RssFeedEntry, ...]:
    """Розбирає RSS-стрічку на нормалізований список матеріалів.
    Разбирает RSS-ленту на нормализованный список материалов.
    """

    entries: list[RssFeedEntry] = []
    channel_element = next(
        (child_element for child_element in list(root_element) if child_element.tag.split("}")[-1] == "channel"),
        None,
    )
    if channel_element is None:
        return ()

    for item_element in list(channel_element):
        if item_element.tag.split("}")[-1] != "item":
            continue
        title_text = extract_xml_child_text(item_element, "title")
        link_url = extract_xml_child_text(item_element, "link")
        published_at_text = normalize_feed_publication_text(extract_xml_child_text(item_element, "pubDate"))
        if not title_text or not link_url:
            continue
        entries.append(
            RssFeedEntry(
                title_text=title_text,
                link_url=link_url,
                published_at_text=published_at_text,
            )
        )
    return tuple(entries)
