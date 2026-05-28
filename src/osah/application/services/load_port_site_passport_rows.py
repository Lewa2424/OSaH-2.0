from pathlib import Path

from osah.domain.entities.port_site_passport_row import PortSitePassportRow
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_port_site_passport_rows import list_port_site_passport_rows


# ###### ЗАВАНТАЖЕННЯ ПАСПОРТІВ ПОРТ-Р / LOAD PORT-R PASSPORTS ######
def load_port_site_passport_rows(
    database_path: Path,
    *,
    include_archived: bool = False,
) -> tuple[PortSitePassportRow, ...]:
    """Завантажує паспорти ділянок ПОРТ-Р з локальної бази.
    Loads PORT-R site passports from the local database.
    """

    connection = create_database_connection(database_path)
    try:
        return list_port_site_passport_rows(connection, include_archived=include_archived)
    finally:
        connection.close()
