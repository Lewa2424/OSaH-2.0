from xml.etree.ElementTree import Element


# ###### ВИТЯГ ТЕКСТУ XML-ДОЧІРНЬОГО ВУЗЛА / ИЗВЛЕЧЕНИЕ ТЕКСТА XML-ДОЧЕРНЕГО УЗЛА ######
def extract_xml_child_text(parent_element: Element, child_name: str) -> str:
    """Повертає текст дочірнього XML-вузла без прив'язки до namespace.
    Возвращает текст дочернего XML-узла без привязки к namespace.
    """

    for child_element in list(parent_element):
        if child_element.tag.split("}")[-1] == child_name:
            return (child_element.text or "").strip()
    return ""
