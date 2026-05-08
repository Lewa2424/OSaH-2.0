from sqlite3 import Connection


def archive_training_record_row(
    connection: Connection,
    record_id: int,
    archive_reason: str,
    replaced_by_record_id: int | None = None,
) -> None:
    """Архівує training-запис і фіксує причину заміни.
    Archives a training record and stores the replacement reason.
    """

    connection.execute(
        """
        UPDATE trainings
        SET
            is_current = 0,
            archived_at = CURRENT_TIMESTAMP,
            archive_reason = ?,
            replaced_by_record_id = ?
        WHERE id = ?;
        """,
        (archive_reason, replaced_by_record_id, record_id),
    )
