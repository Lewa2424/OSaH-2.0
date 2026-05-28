"""Одноразовий скрипт для (пере)генерації тегів реєстру ризиків ПОРТ-Р.
One-off script to (re)generate PORT-R risk registry tags.
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema
from osah.infrastructure.database.seed.seed_port_risk_registry import seed_port_risk_registry
from osah.infrastructure.database.seed.seed_port_risk_registry_tags import seed_port_risk_registry_tags


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed PORT-R risk tags")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Перегенерувати теги навіть якщо вони вже існують",
    )
    args = parser.parse_args()

    paths = build_application_paths(PROJECT_ROOT)
    xlsx_path = PROJECT_ROOT / "for_data" / "Ризики в порту.xlsx"

    connection = create_database_connection(paths.database_file_path)
    try:
        ensure_core_schema(connection)
        seed_port_risk_registry(connection, xlsx_path)
        links_count = seed_port_risk_registry_tags(connection, force=args.force)
        connection.commit()
    finally:
        connection.close()

    print(f"Готово. Зв'язок ризик-тег: {links_count}")


if __name__ == "__main__":
    main()
