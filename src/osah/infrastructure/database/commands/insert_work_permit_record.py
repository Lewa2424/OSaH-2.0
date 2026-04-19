from sqlite3 import Connection

from osah.domain.entities.work_permit_record import WorkPermitRecord


# ###### ДОДАВАННЯ НАРЯДУ-ДОПУСКУ / ДОБАВЛЕНИЕ НАРЯДА-ДОПУСКА ######
def insert_work_permit_record(connection: Connection, work_permit_record: WorkPermitRecord) -> int:
    """Зберігає новий наряд-допуск і повертає його ідентифікатор.
    Сохраняет новый наряд-допуск и возвращает его идентификатор.
    """

    cursor = connection.execute(
        """
        INSERT INTO work_permits (
            permit_number,
            work_kind,
            work_location,
            starts_at,
            ends_at,
            responsible_person,
            issuer_person,
            note_text,
            closed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            work_permit_record.permit_number,
            work_permit_record.work_kind,
            work_permit_record.work_location,
            work_permit_record.starts_at,
            work_permit_record.ends_at,
            work_permit_record.responsible_person,
            work_permit_record.issuer_person,
            work_permit_record.note_text,
            work_permit_record.closed_at,
        ),
    )
    return int(cursor.lastrowid)
