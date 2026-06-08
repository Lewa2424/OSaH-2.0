import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from sqlite3 import Connection

from osah.infrastructure.database.seed.port_risk_registry_records import (
    PORT_RISK_REGISTRY_RECORDS,
)


_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_CODE_RE = re.compile(r"^(\d+\.\d+\.\d+)")


# ###### ЗАСІВ РЕЄСТРУ РИЗИКІВ ПОРТ-Р / SEED PORT-R RISK REGISTRY ######
def seed_port_risk_registry(connection: Connection, xlsx_path: Path) -> int:
    """Завантажує реєстр портових ризиків у базу даних (один раз).
    Loads the port risk registry into the database (once only).

    Спочатку використовує вбудований seed; Excel — лише dev-fallback.
    Uses embedded seed first; Excel is a dev-only fallback.

    Повертає кількість доданих записів.
    Returns the number of inserted records.
    """

    if _registry_is_populated(connection):
        return 0

    records = list(PORT_RISK_REGISTRY_RECORDS)
    if not records and xlsx_path.is_file():
        records = _parse_xlsx(xlsx_path)
    if not records:
        return 0

    return _insert_records(connection, records)


def _insert_records(connection: Connection, records: list[tuple]) -> int:
    connection.executemany(
        """
        INSERT OR IGNORE INTO port_risk_registry (
            risk_code,
            level_1,
            level_2,
            level_3,
            risk_situation,
            hazard_source,
            occurrence_conditions,
            consequences,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        records,
    )
    return len(records)


def _registry_is_populated(connection: Connection) -> bool:
    row = connection.execute("SELECT 1 FROM port_risk_registry LIMIT 1;").fetchone()
    return row is not None


def _parse_xlsx(xlsx_path: Path) -> list[tuple]:
    sst = _read_shared_strings(xlsx_path)
    raw_rows = _read_worksheet_rows(xlsx_path, sst)

    records: list[tuple] = []
    cur_l1 = ""
    cur_l2 = ""
    seen_codes: set[str] = set()
    idx = 0

    for raw in raw_rows[1:]:  # пропускаємо заголовок / skip header
        while len(raw) < 9:
            raw.append("")

        _code_col, l1, l2, l3, sit, src, cond, cons, notes = (v.strip() for v in raw[:9])

        l1 = _normalize_whitespace(l1)
        l2 = _normalize_whitespace(l2)
        l3 = _normalize_whitespace(l3)

        if l1:
            cur_l1 = l1
        if l2:
            cur_l2 = l2
        if not l3:
            continue

        risk_code = _extract_code(l3, idx)
        while risk_code in seen_codes:
            idx += 1
            risk_code = f"auto-{idx}"
        seen_codes.add(risk_code)
        idx += 1

        records.append((
            risk_code,
            cur_l1,
            cur_l2,
            l3,
            sit,
            src,
            cond,
            cons,
            notes,
        ))

    return records


def _extract_code(level_3_text: str, fallback_idx: int) -> str:
    """Витягує числовий код типу '1.1.1' з тексту рівня 3.
    Extracts a numeric code like '1.1.1' from the level-3 text.
    """
    match = _CODE_RE.match(level_3_text)
    if match:
        return match.group(1)
    return f"auto-{fallback_idx}"


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _read_shared_strings(xlsx_path: Path) -> list[str]:
    with zipfile.ZipFile(xlsx_path) as z:
        if "xl/sharedStrings.xml" not in z.namelist():
            return []
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return [
        "".join((t.text or "") for t in si.iter(_NS + "t"))
        for si in root.iter(_NS + "si")
    ]


def _read_worksheet_rows(xlsx_path: Path, sst: list[str]) -> list[list[str]]:
    with zipfile.ZipFile(xlsx_path) as z:
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))

    rows: list[list[str]] = []
    for row_el in root.iter(_NS + "row"):
        vals: list[str] = []
        for c in row_el.iter(_NS + "c"):
            cell_type = c.attrib.get("t")
            v_el = c.find(_NS + "v")
            if v_el is None:
                vals.append("")
                continue
            text = v_el.text or ""
            if cell_type == "s":
                try:
                    text = sst[int(text)]
                except (IndexError, ValueError):
                    pass
            vals.append(text)
        rows.append(vals)
    return rows
