from sqlite3 import Connection

from osah.domain.entities.port_macrovariable import PortMacrovariable
from osah.domain.entities.port_shift_checklist_detail import (
    PortShiftChecklistDetail,
    PortShiftTriggeredItem,
)
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


# ###### ДЕТАЛІ ОЦІНКИ ЗМІНИ ПОРТ-Р / PORT-R SHIFT ASSESSMENT DETAIL ######
def load_port_shift_checklist_detail(
    connection: Connection,
    checklist_id: int,
) -> PortShiftChecklistDetail | None:
    """Повертає заголовок оцінки зміни та перелік фактично спрацьованих блоків з текстами тригерів.
    Returns the shift-assessment header and the list of actually-triggered blocks with trigger texts.
    """

    header = connection.execute(
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
            c.created_at
        FROM port_shift_checklists c
        JOIN port_site_passports p ON p.id = c.passport_id
        LEFT JOIN port_compensating_barriers b ON b.id = c.active_barrier_id
        WHERE c.id = ?;
        """,
        (checklist_id,),
    ).fetchone()

    if header is None:
        return None

    item_rows = connection.execute(
        """
        SELECT
            ci.macrovariable AS macrovariable,
            ci.threshold_id AS threshold_id,
            COALESCE(t.trigger_text, '') AS trigger_text,
            ci.k_used AS k_used,
            COALESCE(t.is_stop_trigger, 0) AS is_stop_trigger
        FROM port_shift_checklist_items ci
        LEFT JOIN port_macrovariable_thresholds t ON t.id = ci.threshold_id
        WHERE ci.checklist_id = ? AND ci.is_triggered = 1
        ORDER BY ci.macrovariable ASC, ci.id ASC;
        """,
        (checklist_id,),
    ).fetchall()

    triggered_items = tuple(
        PortShiftTriggeredItem(
            macrovariable=_parse_macrovariable(row["macrovariable"]),
            threshold_id=int(row["threshold_id"]) if row["threshold_id"] is not None else None,
            trigger_text=str(row["trigger_text"] or ""),
            k_used=float(row["k_used"] or 1.0),
            is_stop_trigger=bool(row["is_stop_trigger"]),
        )
        for row in item_rows
    )

    return PortShiftChecklistDetail(
        row=_header_to_row(header),
        triggered_items=triggered_items,
    )


def _header_to_row(row: object) -> PortShiftChecklistRow:
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
        zone=_parse_zone(str(row["zone"] or "")),
        decision=_parse_decision(str(row["decision"] or "")),
        active_barrier_name=str(row["active_barrier_name"] or ""),
        stop_reason=str(row["stop_reason"] or ""),
        triggered_macrovariables="",
        created_at=str(row["created_at"] or ""),
    )


def _parse_macrovariable(value: object) -> PortMacrovariable:
    try:
        return PortMacrovariable(str(value or "T"))
    except ValueError:
        return PortMacrovariable.T


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
