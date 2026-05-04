from sqlite3 import Connection

from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_exam_basis import MedicalExamBasis
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.evaluate_medical_status import evaluate_medical_status


# ###### ЧТЕНИЕ МЕДИЦИНСКОЙ ЗАПИСИ ПО ID / GET MEDICAL RECORD BY ID ######
def get_medical_record_by_id(connection: Connection, record_id: int) -> MedicalRecord | None:
    """Возвращает одну медицинскую запись по идентификатору.
    Returns one medical record by identifier.
    """

    row = connection.execute(
        """
        SELECT
            medical_records.id,
            medical_records.employee_personnel_number,
            employees.full_name,
            medical_records.valid_from,
            medical_records.valid_until,
            medical_records.medical_decision,
            medical_records.restriction_note,
            medical_records.medical_exam_basis,
            medical_records.basis_text,
            medical_records.basis_note
        FROM medical_records
        INNER JOIN employees
            ON employees.personnel_number = medical_records.employee_personnel_number
        WHERE medical_records.id = ?;
        """,
        (record_id,),
    ).fetchone()
    if row is None:
        return None

    record = MedicalRecord(
        record_id=int(row["id"]),
        employee_personnel_number=row["employee_personnel_number"],
        employee_full_name=row["full_name"],
        valid_from=row["valid_from"],
        valid_until=row["valid_until"],
        medical_decision=MedicalDecision(row["medical_decision"]),
        restriction_note=row["restriction_note"] or "",
        status=MedicalStatus.CURRENT,
        medical_exam_basis=MedicalExamBasis(row["medical_exam_basis"] or "legacy_not_tracked"),
        basis_text=row["basis_text"] or "",
        basis_note=row["basis_note"] or "",
    )
    return MedicalRecord(
        record_id=record.record_id,
        employee_personnel_number=record.employee_personnel_number,
        employee_full_name=record.employee_full_name,
        valid_from=record.valid_from,
        valid_until=record.valid_until,
        medical_decision=record.medical_decision,
        restriction_note=record.restriction_note,
        status=evaluate_medical_status(record),
        medical_exam_basis=record.medical_exam_basis,
        basis_text=record.basis_text,
        basis_note=record.basis_note,
    )
