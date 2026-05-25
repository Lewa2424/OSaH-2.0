from sqlite3 import Connection

from osah.domain.entities.import_batch_summary import ImportBatchSummary


# ###### ЧИТАННЯ ПІДСУМКУ ПАРТІЇ ІМПОРТУ ЗА ID / READ IMPORT BATCH SUMMARY BY ID ######
def get_import_batch_summary_by_id(connection: Connection, batch_id: int) -> ImportBatchSummary | None:
    """Повертає підсумок партії імпорту за її ідентифікатором.
    Returns import batch summary by its identifier.
    """

    row = connection.execute(
        """
        SELECT
            id,
            source_name,
            source_format,
            entity_scope,
            draft_total,
            valid_total,
            invalid_total,
            applied_at,
            created_at
        FROM import_batches
        WHERE id = ?
        LIMIT 1;
        """,
        (batch_id,),
    ).fetchone()
    if row is None:
        return None

    return ImportBatchSummary(
        batch_id=int(row["id"]),
        source_name=row["source_name"],
        source_format=row["source_format"],
        entity_scope=row["entity_scope"],
        draft_total=int(row["draft_total"]),
        valid_total=int(row["valid_total"]),
        invalid_total=int(row["invalid_total"]),
        applied_at=row["applied_at"],
        created_at=row["created_at"],
    )
