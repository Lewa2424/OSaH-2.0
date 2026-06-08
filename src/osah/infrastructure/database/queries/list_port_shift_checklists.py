from sqlite3 import Connection

from osah.domain.entities.port_shift_checklist_row import PortShiftChecklistRow
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


# ###### СПИСОК ЧЕКЛІСТІВ ЗМІН ПОРТ-Р / LIST PORT-R SHIFT CHECKLISTS ######
def list_port_shift_checklists(
    connection: Connection,
    passport_id: int | None = None,
) -> tuple[PortShiftChecklistRow, ...]:
    """Повертає записи журналу відхилень змін ПОРТ-Р (з опціональною фільтрацією за паспортом).
    Returns PORT-R shift deviation log records (optionally filtered by passport).
    """

    if passport_id is not None:
        rows = connection.execute(
            f"""
            SELECT
                c.id,
                c.passport_id,
                p.passport_code,
                p.site_name,
                c.shift_date,
                c.shift_label,
                c.responsible_person,
                c.r_base,
                c.r_dyn,
                c.zone,
                c.decision,
                {_APPLIED_BARRIERS_NAME_SQL.strip()},
                c.stop_reason,
                c.created_at,
                GROUP_CONCAT(DISTINCT ci.macrovariable) AS triggered_macrovariables
            FROM port_shift_checklists c
            JOIN port_site_passports p ON p.id = c.passport_id
            LEFT JOIN port_compensating_barriers b ON b.id = c.active_barrier_id
            LEFT JOIN port_shift_checklist_items ci ON ci.checklist_id = c.id AND ci.is_triggered = 1
            WHERE c.passport_id = ?
            GROUP BY c.id
            ORDER BY c.shift_date DESC, c.id DESC;
            """,
            (passport_id,),
        ).fetchall()
    else:
        rows = connection.execute(
            f"""
            SELECT
                c.id,
                c.passport_id,
                p.passport_code,
                p.site_name,
                c.shift_date,
                c.shift_label,
                c.responsible_person,
                c.r_base,
                c.r_dyn,
                c.zone,
                c.decision,
                {_APPLIED_BARRIERS_NAME_SQL.strip()},
                c.stop_reason,
                c.created_at,
                GROUP_CONCAT(DISTINCT ci.macrovariable) AS triggered_macrovariables
            FROM port_shift_checklists c
            JOIN port_site_passports p ON p.id = c.passport_id
            LEFT JOIN port_compensating_barriers b ON b.id = c.active_barrier_id
            LEFT JOIN port_shift_checklist_items ci ON ci.checklist_id = c.id AND ci.is_triggered = 1
            GROUP BY c.id
            ORDER BY c.shift_date DESC, c.id DESC;
            """,
        ).fetchall()

    return tuple(_row_to_entity(row) for row in rows)


def _row_to_entity(row: object) -> PortShiftChecklistRow:
    zone_raw = str(row["zone"] or "")
    decision_raw = str(row["decision"] or "")
    return PortShiftChecklistRow(
        checklist_id=int(row["id"]),
        passport_id=int(row["passport_id"]),
        passport_code=str(row["passport_code"] or ""),
        site_name=str(row["site_name"] or ""),
        shift_date=str(row["shift_date"] or ""),
        shift_label=str(row["shift_label"] or ""),
        responsible_person=str(row["responsible_person"] or ""),
        r_base=float(row["r_base"] or 1.0),
        r_dyn=float(row["r_dyn"]) if row["r_dyn"] is not None else None,
        zone=_parse_zone(zone_raw),
        decision=_parse_decision(decision_raw),
        active_barrier_name=str(row["active_barrier_name"] or ""),
        stop_reason=str(row["stop_reason"] or ""),
        triggered_macrovariables=str(row["triggered_macrovariables"] or ""),
        created_at=str(row["created_at"] or ""),
    )


def _parse_zone(value: str) -> PortShiftZone | None:
    if not value:
        return None
    try:
        return PortShiftZone(value)
    except ValueError:
        return None


def _parse_decision(value: str) -> PortShiftDecision | None:
    if not value:
        return None
    try:
        return PortShiftDecision(value)
    except ValueError:
        return None
