from sqlite3 import Connection

from osah.domain.entities.import_batch_summary import ImportBatchSummary


# ###### ЧИТАННЯ ОСТАННЬОЇ ПАРТІЇ ІМПОРТУ / ЧТЕНИЕ ПОСЛЕДНЕЙ ПАРТИИ ИМПОРТА ######
def get_latest_import_batch_summary(connection: Connection) -> ImportBatchSummary | None:
    """Повертає підсумок останньої партії імпорту або None.
    Возвращает итог последней партии импорта или None.
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
        ORDER BY id DESC
        LIMIT 1;
        """
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
