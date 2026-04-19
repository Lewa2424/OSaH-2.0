import re
from xml.etree import ElementTree
from zipfile import ZipFile


# ###### ЧИТАННЯ РЯДКІВ XLSX-АРКУША / ЧТЕНИЕ СТРОК XLSX-ЛИСТА ######
def read_xlsx_worksheet_rows(
    archive: ZipFile,
    worksheet_path: str,
    shared_strings: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    """Повертає табличні рядки з XLSX-аркуша у вигляді наборів рядкових значень.
    Возвращает табличные строки из XLSX-листа в виде наборов строковых значений.
    """

    worksheet_xml = archive.read(worksheet_path)
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ElementTree.fromstring(worksheet_xml)
    worksheet_rows: list[tuple[str, ...]] = []
    for row_node in root.findall(".//main:sheetData/main:row", namespace):
        cell_map: dict[int, str] = {}
        max_index = -1
        for cell_node in row_node.findall("main:c", namespace):
            reference = cell_node.attrib.get("r", "")
            column_index = _resolve_xlsx_column_index(reference)
            if column_index < 0:
                continue
            max_index = max(max_index, column_index)
            cell_map[column_index] = _read_xlsx_cell_text(cell_node, shared_strings, namespace)
        if max_index < 0:
            continue
        worksheet_rows.append(tuple(cell_map.get(column_index, "") for column_index in range(max_index + 1)))
    return tuple(worksheet_rows)


# ###### ВИЗНАЧЕННЯ ІНДЕКСУ КОЛОНКИ XLSX / ОПРЕДЕЛЕНИЕ ИНДЕКСА КОЛОНКИ XLSX ######
def _resolve_xlsx_column_index(cell_reference: str) -> int:
    """Повертає нульовий індекс колонки за адресою клітинки XLSX.
    Возвращает нулевой индекс колонки по адресу ячейки XLSX.
    """

    match = re.match(r"([A-Z]+)", cell_reference)
    if match is None:
        return -1

    column_name = match.group(1)
    column_index = 0
    for character in column_name:
        column_index = column_index * 26 + (ord(character) - ord("A") + 1)
    return column_index - 1


# ###### ЧИТАННЯ ТЕКСТУ КЛІТИНКИ XLSX / ЧТЕНИЕ ТЕКСТА ЯЧЕЙКИ XLSX ######
def _read_xlsx_cell_text(
    cell_node: ElementTree.Element,
    shared_strings: tuple[str, ...],
    namespace: dict[str, str],
) -> str:
    """Повертає текстове значення клітинки XLSX.
    Возвращает текстовое значение ячейки XLSX.
    """

    cell_type = cell_node.attrib.get("t", "")
    value_node = cell_node.find("main:v", namespace)
    if value_node is None or value_node.text is None:
        inline_text_node = cell_node.find("main:is/main:t", namespace)
        return inline_text_node.text.strip() if inline_text_node is not None and inline_text_node.text else ""

    cell_value = value_node.text.strip()
    if cell_type == "s":
        shared_string_index = int(cell_value)
        return shared_strings[shared_string_index] if 0 <= shared_string_index < len(shared_strings) else ""
    return cell_value
