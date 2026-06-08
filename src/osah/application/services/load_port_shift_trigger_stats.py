from datetime import date, timedelta
from pathlib import Path

from osah.domain.entities.port_shift_trigger_stat import PortShiftTriggerStat
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.aggregate_port_shift_trigger_stats import (
    aggregate_port_shift_trigger_stats,
)


# ###### ЗАВАНТАЖЕННЯ ПОВТОРЮВАНОСТІ ТРИГЕРІВ ПОРТ-Р / LOAD PORT-R TRIGGER RECURRENCE ######
def load_port_shift_trigger_stats(
    database_path: Path,
    period_days: int,
    passport_id: int | None = None,
) -> tuple[PortShiftTriggerStat, ...]:
    """Завантажує статистику повторюваності тригерів за останні period_days днів.
    Loads trigger-recurrence statistics for the last period_days days.
    """

    cutoff_date = (date.today() - timedelta(days=max(1, period_days))).isoformat()
    connection = create_database_connection(database_path)
    try:
        return aggregate_port_shift_trigger_stats(connection, cutoff_date, passport_id=passport_id)
    finally:
        connection.close()
