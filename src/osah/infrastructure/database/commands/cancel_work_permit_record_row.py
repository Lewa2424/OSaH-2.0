from sqlite3 import Connection


# ###### СКАСУВАННЯ НАРЯДУ-ДОПУСКУ / CANCEL WORK PERMIT ######
def cancel_work_permit_record_row(
    connection: Connection,
    record_id: int,
    canceled_at: str,
    cancel_reason_text: str,
) -> None:
    """Позначає наряд-допуск як скасований із причиною.
    Marks a work permit as canceled with a reason.
    """

    connection.execute(
        """
        UPDATE work_permits
        SET canceled_at = ?, cancel_reason_text = ?
        WHERE id = ?;
        """,
        (canceled_at, cancel_reason_text, record_id),
    )
