from sqlite3 import Connection


# ###### ДОДАВАННЯ ПАРТІЇ ІМПОРТУ / ДОБАВЛЕНИЕ ПАРТИИ ИМПОРТА ######
def insert_import_batch(
    connection: Connection,
    source_name: str,
    source_format: str,
    entity_scope: str,
    draft_total: int,
    valid_total: int,
    invalid_total: int,
) -> int:
    """Створює нову партію імпорту й повертає її ідентифікатор.
    Создаёт новую партию импорта и возвращает её идентификатор.
    """

    cursor = connection.execute(
        """
        INSERT INTO import_batches (
            source_name,
            source_format,
            entity_scope,
            draft_total,
            valid_total,
            invalid_total
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            source_name,
            source_format,
            entity_scope,
            draft_total,
            valid_total,
            invalid_total,
        ),
    )
    return int(cursor.lastrowid)
