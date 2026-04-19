from xml.etree import ElementTree
from zipfile import ZipFile


# ###### ВИЗНАЧЕННЯ ШЛЯХУ ПЕРШОГО АРКУША XLSX / ОПРЕДЕЛЕНИЕ ПУТИ ПЕРВОГО ЛИСТА XLSX ######
def resolve_first_xlsx_worksheet_path(archive: ZipFile) -> str:
    """Повертає шлях до першого робочого аркуша всередині XLSX-архіву.
    Возвращает путь к первому рабочему листу внутри XLSX-архива.
    """

    workbook_xml = archive.read("xl/workbook.xml")
    relationships_xml = archive.read("xl/_rels/workbook.xml.rels")

    workbook_namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    relationships_namespace = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}

    workbook_root = ElementTree.fromstring(workbook_xml)
    relationships_root = ElementTree.fromstring(relationships_xml)

    first_sheet = workbook_root.find("main:sheets/main:sheet", workbook_namespace)
    if first_sheet is None:
        raise ValueError("У XLSX-файлі не знайдено жодного аркуша.")

    relationship_id = first_sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
    for relationship_node in relationships_root.findall("rel:Relationship", relationships_namespace):
        if relationship_node.attrib.get("Id") == relationship_id:
            target_path = relationship_node.attrib.get("Target", "")
            if not target_path:
                break
            return f"xl/{target_path.lstrip('/')}"

    raise ValueError("Не вдалося визначити перший аркуш XLSX-файлу.")
