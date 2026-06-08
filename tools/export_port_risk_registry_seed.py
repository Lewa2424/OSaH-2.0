"""Експортує реєстр ризиків ПОРТ-Р у вбудований Python-seed.
Exports the PORT-R risk registry into an embedded Python seed module.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    database_path = project_root / "data" / "osah.sqlite3"
    output_path = (
        project_root
        / "src"
        / "osah"
        / "infrastructure"
        / "database"
        / "seed"
        / "port_risk_registry_records.py"
    )

    connection = sqlite3.connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                risk_code,
                level_1,
                level_2,
                level_3,
                risk_situation,
                hazard_source,
                occurrence_conditions,
                consequences,
                notes
            FROM port_risk_registry
            ORDER BY id ASC;
            """
        ).fetchall()
    finally:
        connection.close()

    lines = [
        '"""Вбудований реєстр ризиків ПОРТ-Р / Embedded PORT-R risk registry records."""',
        "",
        "from __future__ import annotations",
        "",
        "PORT_RISK_REGISTRY_RECORDS: tuple[tuple[str, str, str, str, str, str, str, str, str], ...] = (",
    ]
    for row in rows:
        escaped_values = ", ".join(repr(str(value or "")) for value in row)
        lines.append(f"    ({escaped_values}),")
    lines.append(")")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Exported {len(rows)} records to {output_path}")


if __name__ == "__main__":
    main()
