from pathlib import Path

from osah.domain.entities.port_shift_checklist_detail import PortShiftChecklistDetail
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.load_port_shift_checklist_detail import (
    load_port_shift_checklist_detail as query_load_port_shift_checklist_detail,
)


# ###### ЗАВАНТАЖЕННЯ ДЕТАЛЕЙ ОЦІНКИ ЗМІНИ / LOAD SHIFT ASSESSMENT DETAIL ######
def load_port_shift_checklist_detail(
    database_path: Path,
    checklist_id: int,
) -> PortShiftChecklistDetail | None:
    """Завантажує повну картку однієї оцінки зміни ПОРТ-Р за її ідентифікатором.
    Loads the full card of a single PORT-R shift assessment by its identifier.
    """

    connection = create_database_connection(database_path)
    try:
        return query_load_port_shift_checklist_detail(connection, checklist_id)
    finally:
        connection.close()
