from sqlite3 import Connection

from osah.domain.entities.port_macrovariable import PortMacrovariable
from osah.domain.entities.port_shift_trigger_stat import PortShiftTriggerStat


# ###### АГРЕГАЦІЯ ПОВТОРЮВАНОСТІ ТРИГЕРІВ ПОРТ-Р / AGGREGATE PORT-R TRIGGER RECURRENCE ######
def aggregate_port_shift_trigger_stats(
    connection: Connection,
    cutoff_date: str,
    passport_id: int | None = None,
) -> tuple[PortShiftTriggerStat, ...]:
    """Рахує, скільки разів кожен тригер спрацював у журналі змін за період (з опц. фільтром за паспортом).
    Counts how many times each trigger fired in the shift log over a period (optional passport filter).

    cutoff_date — нижня межа shift_date у форматі РРРР-ММ-ДД (включно).
    cutoff_date is the lower bound of shift_date in YYYY-MM-DD format (inclusive).
    """

    base_sql = """
        SELECT
            t.id AS threshold_id,
            t.passport_id AS passport_id,
            p.passport_code AS passport_code,
            p.site_name AS site_name,
            ci.macrovariable AS macrovariable,
            t.trigger_text AS trigger_text,
            t.is_stop_trigger AS is_stop_trigger,
            COUNT(ci.id) AS hit_count,
            MAX(c.shift_date) AS last_shift_date
        FROM port_shift_checklist_items ci
        JOIN port_shift_checklists c ON c.id = ci.checklist_id
        JOIN port_macrovariable_thresholds t ON t.id = ci.threshold_id
        JOIN port_site_passports p ON p.id = t.passport_id
        WHERE ci.is_triggered = 1
          AND ci.threshold_id IS NOT NULL
          AND c.shift_date >= ?
    """

    params: list[object] = [cutoff_date]
    if passport_id is not None:
        base_sql += " AND c.passport_id = ?"
        params.append(passport_id)

    base_sql += """
        GROUP BY ci.threshold_id
        ORDER BY hit_count DESC, last_shift_date DESC;
    """

    rows = connection.execute(base_sql, params).fetchall()
    return tuple(_row_to_entity(row) for row in rows)


def _row_to_entity(row: object) -> PortShiftTriggerStat:
    return PortShiftTriggerStat(
        passport_id=int(row["passport_id"]),
        passport_code=str(row["passport_code"] or ""),
        site_name=str(row["site_name"] or ""),
        macrovariable=_parse_macrovariable(row["macrovariable"]),
        threshold_id=int(row["threshold_id"]),
        trigger_text=str(row["trigger_text"] or ""),
        is_stop_trigger=bool(row["is_stop_trigger"]),
        hit_count=int(row["hit_count"] or 0),
        last_shift_date=str(row["last_shift_date"] or ""),
    )


def _parse_macrovariable(value: object) -> PortMacrovariable:
    try:
        return PortMacrovariable(str(value or "T"))
    except ValueError:
        return PortMacrovariable.T
