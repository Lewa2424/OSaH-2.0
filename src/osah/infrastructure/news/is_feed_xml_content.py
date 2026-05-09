from xml.etree import ElementTree


# ###### ПЕРЕВІРКА XML НА RSS/ATOM / ПРОВЕРКА XML НА RSS/ATOM ######
def is_feed_xml_content(xml_content_text: str) -> bool:
    """Повертає True, якщо текст є RSS або Atom XML-стрічкою.
    Возвращает True, если текст является RSS или Atom XML-лентой.
    """

    try:
        root_element = ElementTree.fromstring(xml_content_text.lstrip())
    except ElementTree.ParseError:
        return False
    root_tag_name = root_element.tag.split("}")[-1]
    return root_tag_name in {"rss", "feed"}
