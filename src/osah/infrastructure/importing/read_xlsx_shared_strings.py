from xml.etree import ElementTree
from zipfile import ZipFile


# ###### ЧИТАННЯ SHARED STRINGS XLSX / ЧТЕНИЕ SHARED STRINGS XLSX ######
def read_xlsx_shared_strings(archive: ZipFile) -> tuple[str, ...]:
    """Повертає таблицю shared strings з XLSX-архіву.
    Возвращает таблицу shared strings из XLSX-архива.
    """

    try:
        shared_strings_xml = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return ()

    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ElementTree.fromstring(shared_strings_xml)
    shared_strings: list[str] = []
    for shared_string_node in root.findall("main:si", namespace):
        text_parts = [text_node.text or "" for text_node in shared_string_node.findall(".//main:t", namespace)]
        shared_strings.append("".join(text_parts))
    return tuple(shared_strings)
