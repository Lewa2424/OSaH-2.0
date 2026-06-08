from pathlib import Path

from osah.domain.entities.port_passport_calibration import PortPassportCalibration
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.load_port_calibration import load_port_calibration


# ###### ЗАВАНТАЖЕННЯ КАЛІБРУВАННЯ ПАСПОРТА ПОРТ-Р / LOAD PORT-R PASSPORT CALIBRATION ######
def load_port_calibration_for_passport(
    database_path: Path,
    passport_id: int,
) -> PortPassportCalibration:
    """Завантажує калібрування динамічного контуру паспорта (пороги Т-П-С-В-Б і компенсуючі бар'єри).
    Loads the dynamic-circuit calibration for a passport (T-P-S-V-B thresholds and compensating barriers).
    """

    connection = create_database_connection(database_path)
    try:
        return load_port_calibration(connection, passport_id)
    finally:
        connection.close()
