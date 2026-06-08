from sqlite3 import Connection

from osah.domain.entities.port_passport_calibration import PortPassportCalibration


# ###### ЗБЕРЕЖЕННЯ КАЛІБРУВАННЯ ПАСПОРТА ПОРТ-Р / SAVE PORT-R PASSPORT CALIBRATION ######
def save_port_calibration(
    connection: Connection,
    calibration: PortPassportCalibration,
) -> None:
    """Зберігає калібрування динамічного контуру: оновлює r_base, замінює пороги і компенсуючі бар'єри.
    Saves the dynamic-circuit calibration: updates r_base, replaces thresholds and compensating barriers.

    Використовує DELETE + INSERT замість upsert для збереження порядку рядків і простоти логіки.
    Uses DELETE + INSERT instead of upsert to preserve row ordering and simplify logic.
    """

    connection.execute(
        "UPDATE port_site_passports SET r_base = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
        (calibration.r_base, calibration.passport_id),
    )

    connection.execute(
        "DELETE FROM port_macrovariable_thresholds WHERE passport_id = ?;",
        (calibration.passport_id,),
    )
    for threshold in calibration.thresholds:
        connection.execute(
            """
            INSERT INTO port_macrovariable_thresholds
                (passport_id, macrovariable, trigger_text, k_value, is_stop_trigger)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                calibration.passport_id,
                threshold.macrovariable.value,
                threshold.trigger_text,
                threshold.k_value,
                int(threshold.is_stop_trigger),
            ),
        )

    connection.execute(
        "DELETE FROM port_compensating_barriers WHERE passport_id = ?;",
        (calibration.passport_id,),
    )
    for barrier in calibration.compensating_barriers:
        connection.execute(
            """
            INSERT INTO port_compensating_barriers
                (passport_id, macrovariable, barrier_name, description, k_comp)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                calibration.passport_id,
                barrier.macrovariable.value,
                barrier.barrier_name,
                barrier.description,
                barrier.k_comp,
            ),
        )
