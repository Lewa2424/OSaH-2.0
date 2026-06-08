import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class KeyIssueRecordRow:
    """Рядок реєстру виданих ключів / Issued key registry row."""

    record_id: int
    created_at: str
    customer: str
    contact: str
    installation_id: str
    key_kind: str
    previous_record_id: int | None
    note: str
    paste_token: str


# ###### СПИСОК ВИДАНИХ КЛЮЧІВ / LIST ISSUED KEY RECORDS ######
def list_key_issue_records(database_path: Path) -> tuple[KeyIssueRecordRow, ...]:
    """Повертає всі записи реєстру виданих ключів.
    Returns all issued setup key registry records.
    """

    connection = sqlite3.connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                id,
                created_at,
                customer,
                contact,
                installation_id,
                key_kind,
                previous_record_id,
                note,
                paste_token
            FROM key_issue_records
            ORDER BY id DESC;
            """
        ).fetchall()
    finally:
        connection.close()

    return tuple(
        KeyIssueRecordRow(
            record_id=int(row[0]),
            created_at=str(row[1]),
            customer=str(row[2]),
            contact=str(row[3]),
            installation_id=str(row[4]),
            key_kind=str(row[5]),
            previous_record_id=int(row[6]) if row[6] is not None else None,
            note=str(row[7]),
            paste_token=str(row[8]),
        )
        for row in rows
    )
