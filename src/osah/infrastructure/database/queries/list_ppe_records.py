from sqlite3 import Connection

from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.evaluate_ppe_status import evaluate_ppe_status


# ###### ЧТЕНИЕ РЕЕСТРА СИЗ / LIST PPE RECORDS ######
def list_ppe_records(connection: Connection) -> tuple[PpeRecord, ...]:
    """Возвращает все записи СИЗ с расширенными полями и статусами.
    Returns all PPE records with extended fields and calculated statuses.
    """

    rows = connection.execute(
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
        ORDER BY employees.full_name COLLATE NOCASE ASC, ppe_records.ppe_name COLLATE NOCASE ASC, ppe_records.id ASC;
        """
    ).fetchall()

    records: list[PpeRecord] = []
    for row in rows:
        ppe_record = PpeRecord(
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
            compliance_check_state=PpeComplianceCheckState(
                row["compliance_check_state"] or "legacy_not_tracked"
            ),
            basis_text=row["basis_text"] or "",
            basis_note=row["basis_note"] or "",
        )
        records.append(
            PpeRecord(
                record_id=ppe_record.record_id,
                employee_personnel_number=ppe_record.employee_personnel_number,
                employee_full_name=ppe_record.employee_full_name,
                ppe_name=ppe_record.ppe_name,
                is_required=ppe_record.is_required,
                is_issued=ppe_record.is_issued,
                issue_date=ppe_record.issue_date,
                replacement_date=ppe_record.replacement_date,
                quantity=ppe_record.quantity,
                note_text=ppe_record.note_text,
                status=evaluate_ppe_status(ppe_record),
                provision_status=ppe_record.provision_status,
                compliance_check_state=ppe_record.compliance_check_state,
                basis_text=ppe_record.basis_text,
                basis_note=ppe_record.basis_note,
            )
        )

    return tuple(records)
