from sqlite3 import Connection

from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.evaluate_ppe_status import evaluate_ppe_status


# ###### ЧИТАННЯ ЗАПИСУ ЗІЗ ЗА ID / READ PPE RECORD BY ID ######
def get_ppe_record_by_id(connection: Connection, record_id: int) -> PpeRecord | None:
    """Повертає один запис ЗІЗ за ідентифікатором.
    Returns one PPE record by identifier.
    """

    row = connection.execute(
        """
        SELECT
            ppe_records.id,
            ppe_records.employee_personnel_number,
            employees.full_name,
            ppe_records.ppe_name,
            ppe_records.is_required,
            ppe_records.is_issued,
            ppe_records.issue_date,
            ppe_records.replacement_date,
            ppe_records.quantity,
            ppe_records.note_text
        FROM ppe_records
        INNER JOIN employees
            ON employees.personnel_number = ppe_records.employee_personnel_number
        WHERE ppe_records.id = ?;
        """,
        (record_id,),
    ).fetchone()
    if row is None:
        return None

    record = PpeRecord(
        record_id=int(row["id"]),
        employee_personnel_number=row["employee_personnel_number"],
        employee_full_name=row["full_name"],
        ppe_name=row["ppe_name"],
        is_required=bool(row["is_required"]),
        is_issued=bool(row["is_issued"]),
        issue_date=row["issue_date"],
        replacement_date=row["replacement_date"],
        quantity=int(row["quantity"]),
        note_text=row["note_text"] or "",
        status=PpeStatus.CURRENT,
    )
    return PpeRecord(
        record_id=record.record_id,
        employee_personnel_number=record.employee_personnel_number,
        employee_full_name=record.employee_full_name,
        ppe_name=record.ppe_name,
        is_required=record.is_required,
        is_issued=record.is_issued,
        issue_date=record.issue_date,
        replacement_date=record.replacement_date,
        quantity=record.quantity,
        note_text=record.note_text,
        status=evaluate_ppe_status(record),
    )
