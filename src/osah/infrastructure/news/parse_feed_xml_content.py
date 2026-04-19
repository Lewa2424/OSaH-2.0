from xml.etree import ElementTree

from osah.domain.entities.rss_feed_entry import RssFeedEntry
from osah.infrastructure.news.parse_atom_feed_entries import parse_atom_feed_entries
from osah.infrastructure.news.parse_rss_feed_entries import parse_rss_feed_entries


# ###### РОЗБІР XML-КОНТЕНТУ FEED / РАЗБОР XML-КОНТЕНТА FEED ######
def parse_feed_xml_content(xml_content_text: str) -> tuple[RssFeedEntry, ...]:
    """Визначає тип стрічки і повертає нормалізовані записи RSS або Atom.
    Определяет тип ленты и возвращает нормализованные записи RSS или Atom.
    """

    root_element = ElementTree.fromstring(xml_content_text)
    root_tag_name = root_element.tag.split("}")[-1]
    if root_tag_name == "rss":
        return parse_rss_feed_entries(root_element)
    if root_tag_name == "feed":
        return parse_atom_feed_entries(root_element)
    return ()
