import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class KeyIssueRecordInput:
    """Вхідні дані для запису виданого ключа / Input for an issued key record."""

    customer: str
    contact: str
    installation_id: str
    key_kind: str
    previous_record_id: int | None
    note: str
    paste_token: str


# ###### ЗАПИС ВИДАНОГО КЛЮЧА / INSERT ISSUED KEY RECORD ######
def insert_key_issue_record(database_path: Path, record_input: KeyIssueRecordInput) -> int:
    """Зберігає виданий ключ установки в локальному реєстрі.
    Stores an issued setup key in the local registry.
    """

    connection = sqlite3.connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO key_issue_records (
                created_at,
                customer,
                contact,
                installation_id,
                key_kind,
                previous_record_id,
                note,
                paste_token
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                record_input.customer.strip(),
                record_input.contact.strip(),
                record_input.installation_id.strip(),
                record_input.key_kind.strip(),
                record_input.previous_record_id,
                record_input.note.strip(),
                record_input.paste_token.strip(),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()
