from sqlite3 import Connection

from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.evaluate_ppe_status import evaluate_ppe_status


# ###### ЧТЕНИЕ ЗАПИСИ СИЗ ПО ID / READ PPE RECORD BY ID ######
def get_ppe_record_by_id(connection: Connection, record_id: int) -> PpeRecord | None:
    """Возвращает один экземпляр записи СИЗ по идентификатору.
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
            ppe_records.note_text,
            ppe_records.provision_status,
            ppe_records.compliance_check_state,
            ppe_records.basis_text,
            ppe_records.basis_note
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
        provision_status=PpeProvisionStatus(row["provision_status"] or "legacy_not_tracked"),
        compliance_check_state=PpeComplianceCheckState(row["compliance_check_state"] or "legacy_not_tracked"),
        basis_text=row["basis_text"] or "",
        basis_note=row["basis_note"] or "",
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
        provision_status=record.provision_status,
        compliance_check_state=record.compliance_check_state,
        basis_text=record.basis_text,
        basis_note=record.basis_note,
    )
