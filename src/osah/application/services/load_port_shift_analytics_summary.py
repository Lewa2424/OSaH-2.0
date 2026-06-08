from datetime import date, timedelta
from pathlib import Path

from osah.domain.entities.port_shift_analytics_summary import PortShiftAnalyticsSummary
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.aggregate_port_shift_analytics_summary import (
    aggregate_port_shift_analytics_summary,
)


# ###### ЗАВАНТАЖЕННЯ ЗВЕДЕННЯ ЖУРНАЛУ ПОРТ-Р / LOAD PORT-R SHIFT LOG SUMMARY ######
def load_port_shift_analytics_summary(
    database_path: Path,
    period_days: int,
    passport_id: int | None = None,
) -> PortShiftAnalyticsSummary:
    """Завантажує зведення журналу оцінок змін за останні period_days днів.
    Loads the shift assessment log summary for the last period_days days.
    """

    cutoff_date = (date.today() - timedelta(days=max(1, period_days))).isoformat()
    connection = create_database_connection(database_path)
    try:
        return aggregate_port_shift_analytics_summary(connection, cutoff_date, passport_id=passport_id)
    finally:
        connection.close()
