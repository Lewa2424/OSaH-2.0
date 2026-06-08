from pathlib import Path

from osah.domain.entities.port_shift_checklist_row import PortShiftChecklistRow
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_port_shift_checklists import list_port_shift_checklists


# ###### ЗАВАНТАЖЕННЯ ЖУРНАЛУ ВІДХИЛЕНЬ ПОРТ-Р / LOAD PORT-R DEVIATION LOG ######
def load_port_shift_checklists(
    database_path: Path,
    passport_id: int | None = None,
) -> tuple[PortShiftChecklistRow, ...]:
    """Завантажує журнал оцінок змін ПОРТ-Р з бази даних.
    Loads the PORT-R shift assessment log from the database.
    """

    connection = create_database_connection(database_path)
    try:
        return list_port_shift_checklists(connection, passport_id=passport_id)
    finally:
        connection.close()
