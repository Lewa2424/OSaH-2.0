import json
from datetime import datetime
from pathlib import Path

from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_user_table_names import list_user_table_names


# ###### ЕКСПОРТ ПОВНОГО СТАНУ СИСТЕМИ / ЭКСПОРТ ПОЛНОГО СОСТОЯНИЯ СИСТЕМЫ ######
def export_full_system_state(database_path: Path) -> Path:
    """Створює JSON-експорт повного стану локальної системи й повертає шлях до файлу.
    Создаёт JSON-экспорт полного состояния локальной системы и возвращает путь к файлу.
    """

    export_directory = database_path.parent / "exports"
    export_directory.mkdir(parents=True, exist_ok=True)
    exported_at = datetime.now()
    export_file_path = export_directory / f"osah-export-{exported_at.strftime('%Y%m%d-%H%M%S')}.json"

    connection = create_database_connection(database_path)
    try:
        exported_tables = {
            table_name: _read_full_table(connection, table_name)
            for table_name in list_user_table_names(connection)
        }
        insert_audit_log(
            connection,
            event_type="export.full",
            module_name="import_export",
            event_level="info",
            actor_name="system",
            entity_name=str(export_file_path.name),
            result_status="success",
            description_text=f"tables={len(exported_tables)};exported_at={exported_at.isoformat()}",
        )
        connection.commit()
    finally:
        connection.close()

    export_payload = {
        "format_version": 1,
        "exported_at": exported_at.isoformat(),
        "database_file_name": database_path.name,
        "tables": exported_tables,
    }
    export_file_path.write_text(
        json.dumps(export_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return export_file_path


# ###### ЧИТАННЯ ПОВНОЇ ТАБЛИЦІ ДЛЯ ЕКСПОРТУ / ЧТЕНИЕ ПОЛНОЙ ТАБЛИЦЫ ДЛЯ ЭКСПОРТА ######
def _read_full_table(connection, table_name: str) -> list[dict[str, object]]:
    """Повертає всі рядки таблиці у вигляді JSON-сумісних словників.
    Возвращает все строки таблицы в виде JSON-совместимых словарей.
    """

    rows = connection.execute(f"SELECT * FROM {table_name};").fetchall()
    return [dict(row) for row in rows]
