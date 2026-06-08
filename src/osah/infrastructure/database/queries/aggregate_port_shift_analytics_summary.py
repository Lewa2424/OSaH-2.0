from sqlite3 import Connection

from osah.domain.entities.port_shift_analytics_summary import PortShiftAnalyticsSummary
from osah.domain.entities.port_shift_decision import PortShiftDecision
from osah.domain.entities.port_shift_zone import PortShiftZone


# ###### ЗВЕДЕННЯ ЖУРНАЛУ ЗМІН ПОРТ-Р / PORT-R SHIFT LOG SUMMARY ######
def aggregate_port_shift_analytics_summary(
    connection: Connection,
    cutoff_date: str,
    passport_id: int | None = None,
) -> PortShiftAnalyticsSummary:
    """Повертає зведення журналу оцінок змін за період: кількість зон, STOP і середній R_dyn.
    Returns the shift log summary over a period: zone counts, STOP count, and average R_dyn.

    cutoff_date — нижня межа shift_date у форматі РРРР-ММ-ДД (включно).
    cutoff_date is the lower bound of shift_date in YYYY-MM-DD format (inclusive).
    """

    base_sql = """
        SELECT
            COUNT(*) AS assessments_count,
            SUM(CASE WHEN zone = ? THEN 1 ELSE 0 END) AS green_count,
            SUM(CASE WHEN zone = ? THEN 1 ELSE 0 END) AS yellow_count,
            SUM(CASE WHEN zone = ? THEN 1 ELSE 0 END) AS red_count,
            SUM(CASE WHEN decision = ? THEN 1 ELSE 0 END) AS stop_count,
            AVG(r_dyn) AS avg_r_dyn
        FROM port_shift_checklists
        WHERE shift_date >= ?
    """

    params: list[object] = [
        PortShiftZone.GREEN.value,
        PortShiftZone.YELLOW.value,
        PortShiftZone.RED.value,
        PortShiftDecision.STOP.value,
        cutoff_date,
    ]
    if passport_id is not None:
        base_sql += " AND passport_id = ?"
        params.append(passport_id)

    row = connection.execute(base_sql, params).fetchone()

    avg_raw = row["avg_r_dyn"] if row is not None else None
    return PortShiftAnalyticsSummary(
        assessments_count=int(row["assessments_count"] or 0) if row else 0,
        green_count=int(row["green_count"] or 0) if row else 0,
        yellow_count=int(row["yellow_count"] or 0) if row else 0,
        red_count=int(row["red_count"] or 0) if row else 0,
        stop_count=int(row["stop_count"] or 0) if row else 0,
        avg_r_dyn=float(avg_raw) if avg_raw is not None else None,
    )
