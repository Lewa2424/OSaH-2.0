from pathlib import Path

from osah.domain.entities.port_site_risk import PortSiteRisk
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_port_site_risks_for_passport import list_port_site_risks_for_passport


# ###### ЗАВАНТАЖЕННЯ РИЗИКІВ ПАСПОРТА ПОРТ-Р / LOAD PORT-R PASSPORT RISKS ######
def load_port_site_risks_for_passport(
    database_path: Path,
    passport_id: int,
) -> tuple[PortSiteRisk, ...]:
    """Завантажує ризики паспорта ділянки з бази даних.
    Loads site passport risks from the database.
    """

    connection = create_database_connection(database_path)
    try:
        return list_port_site_risks_for_passport(connection, passport_id)
    finally:
        connection.close()
