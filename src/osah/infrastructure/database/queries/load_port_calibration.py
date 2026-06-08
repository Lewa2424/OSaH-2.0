from sqlite3 import Connection

from osah.domain.entities.port_compensating_barrier_item import PortCompensatingBarrierItem
from osah.domain.entities.port_macrovariable import PortMacrovariable
from osah.domain.entities.port_macrovariable_threshold import PortMacrovariableThreshold
from osah.domain.entities.port_passport_calibration import PortPassportCalibration


# ###### ЗАВАНТАЖЕННЯ КАЛІБРУВАННЯ ПАСПОРТА ПОРТ-Р / LOAD PORT-R PASSPORT CALIBRATION ######
def load_port_calibration(
    connection: Connection,
    passport_id: int,
) -> PortPassportCalibration:
    """Завантажує калібрування динамічного контуру паспорта: пороги Т-П-С-В-Б і компенсуючі бар'єри.
    Loads the dynamic-circuit calibration for a passport: T-P-S-V-B thresholds and compensating barriers.
    """

    r_base_row = connection.execute(
        "SELECT r_base FROM port_site_passports WHERE id = ?;",
        (passport_id,),
    ).fetchone()
    r_base = float(r_base_row["r_base"]) if r_base_row and r_base_row["r_base"] is not None else 1.0

    threshold_rows = connection.execute(
        """
        SELECT id, passport_id, macrovariable, trigger_text, k_value, is_stop_trigger
        FROM port_macrovariable_thresholds
        WHERE passport_id = ?
        ORDER BY macrovariable ASC, id ASC;
        """,
        (passport_id,),
    ).fetchall()

    thresholds = tuple(
        PortMacrovariableThreshold(
            threshold_id=int(row["id"]),
            passport_id=int(row["passport_id"]),
            macrovariable=_parse_macrovariable(row["macrovariable"]),
            trigger_text=str(row["trigger_text"] or ""),
            k_value=float(row["k_value"] or 1.0),
            is_stop_trigger=bool(row["is_stop_trigger"]),
        )
        for row in threshold_rows
    )

    barrier_rows = connection.execute(
        """
        SELECT id, passport_id, macrovariable, barrier_name, description, k_comp
        FROM port_compensating_barriers
        WHERE passport_id = ?
        ORDER BY macrovariable ASC, id ASC;
        """,
        (passport_id,),
    ).fetchall()

    compensating_barriers = tuple(
        PortCompensatingBarrierItem(
            barrier_id=int(row["id"]),
            passport_id=int(row["passport_id"]),
            barrier_name=str(row["barrier_name"] or ""),
            description=str(row["description"] or ""),
            k_comp=float(row["k_comp"] or 0.9),
            macrovariable=_parse_macrovariable(row["macrovariable"]),
        )
        for row in barrier_rows
    )

    return PortPassportCalibration(
        passport_id=passport_id,
        r_base=r_base,
        thresholds=thresholds,
        compensating_barriers=compensating_barriers,
    )


def _parse_macrovariable(value: object) -> PortMacrovariable:
    try:
        return PortMacrovariable(str(value or "T"))
    except ValueError:
        return PortMacrovariable.T
