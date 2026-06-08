from sqlite3 import Connection

from osah.domain.entities.port_shift_decision import PortShiftDecision
from osah.domain.entities.port_shift_zone import PortShiftZone


_APPLIED_BARRIERS_NAME_SQL = """
COALESCE(
    NULLIF(
        (SELECT GROUP_CONCAT(b_applied.barrier_name, ', ')
         FROM port_shift_checklist_barriers cb_applied
         JOIN port_compensating_barriers b_applied ON b_applied.id = cb_applied.barrier_id
         WHERE cb_applied.checklist_id = c.id),
        ''
    ),
    COALESCE(b.barrier_name, '')
) AS active_barrier_name
"""


# ###### СТВОРЕННЯ ЧЕКЛІСТА ЗМІНИ ПОРТ-Р / INSERT PORT-R SHIFT CHECKLIST ######
def insert_port_shift_checklist(
    connection: Connection,
    passport_id: int,
    shift_date: str,
    shift_label: str,
    responsible_person: str,
    r_base: float,
    r_dyn: float,
    zone: PortShiftZone,
    decision: PortShiftDecision,
    active_barrier_ids: list[int],
    stop_reason: str,
    triggered_threshold_ids: list[int],
    all_macrovariable_k_pairs: list[tuple[str, int | None, float]],
) -> int:
    """Зберігає оцінку зміни ПОРТ-Р та деталі по макрозмінних.
    Saves a PORT-R shift assessment and per-macrovariable details.

    all_macrovariable_k_pairs — список (macrovariable, threshold_id | None, k_used)
    для всіх поточних тригерів (і спрацьованих, і штатних).
    """

    cursor = connection.execute(
        """
        INSERT INTO port_shift_checklists (
            passport_id, shift_date, shift_label, responsible_person,
            r_base, r_dyn, zone, decision, active_barrier_id, stop_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            passport_id,
            shift_date,
            shift_label,
            responsible_person,
            r_base,
            r_dyn,
            zone.value,
            decision.value,
            active_barrier_ids[0] if active_barrier_ids else None,
            stop_reason,
        ),
    )
    checklist_id = int(cursor.lastrowid)

    for barrier_id in active_barrier_ids:
        connection.execute(
            """
            INSERT INTO port_shift_checklist_barriers (checklist_id, barrier_id)
            VALUES (?, ?);
            """,
            (checklist_id, barrier_id),
        )

    for macrovariable, threshold_id, k_used in all_macrovariable_k_pairs:
        is_triggered = threshold_id in triggered_threshold_ids if threshold_id is not None else False
        connection.execute(
            """
            INSERT INTO port_shift_checklist_items
                (checklist_id, macrovariable, threshold_id, is_triggered, k_used)
            VALUES (?, ?, ?, ?, ?);
            """,
            (checklist_id, macrovariable, threshold_id, int(is_triggered), k_used),
        )

    return checklist_id
