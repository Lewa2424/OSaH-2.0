from xml.etree.ElementTree import Element

from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.infrastructure.news.extract_xml_child_text import extract_xml_child_text
from osah.infrastructure.news.normalize_feed_publication_text import normalize_feed_publication_text


# ###### РОЗБІР ATOM-СТРІЧКИ / РАЗБОР ATOM-ЛЕНТЫ ######
def parse_atom_feed_entries(root_element: Element) -> tuple[RssFeedEntry, ...]:
    """Розбирає Atom-стрічку на нормалізований список матеріалів.
    Разбирает Atom-ленту на нормализованный список материалов.
    """

    entries: list[RssFeedEntry] = []
    for entry_element in list(root_element):
        if entry_element.tag.split("}")[-1] != "entry":
            continue
        link_url = ""
        for child_element in list(entry_element):
            if child_element.tag.split("}")[-1] == "link":
                link_url = (child_element.attrib.get("href", "") or "").strip()
                if link_url:
                    break
        title_text = extract_xml_child_text(entry_element, "title")
        published_at_text = normalize_feed_publication_text(
            extract_xml_child_text(entry_element, "updated") or extract_xml_child_text(entry_element, "published")
        )
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
