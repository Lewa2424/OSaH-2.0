from sqlite3 import Connection

from osah.domain.entities.work_permit_daily_check import WorkPermitDailyCheck


def insert_work_permit_daily_check(
    connection: Connection,
    work_permit_id: int,
    daily_check: WorkPermitDailyCheck,
) -> None:
    """Додає щоденну перевірку до журналу наряду-допуску.
    Inserts a daily check into the work-permit journal.
    """

    connection.execute(
        """
        INSERT INTO work_permit_daily_checks (
            work_permit_id,
            checked_at,
            checked_by,
            note_text
        )
        VALUES (?, ?, ?, ?);
        """,
        (
            work_permit_id,
            daily_check.checked_at,
            daily_check.checked_by,
            daily_check.note_text,
        ),
    )
