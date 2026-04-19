from sqlite3 import Connection

from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.evaluate_medical_status import evaluate_medical_status


# ###### ЧИТАННЯ РЕЄСТРУ МЕДИЦИНИ / ЧТЕНИЕ РЕЕСТРА МЕДИЦИНЫ ######
def list_medical_records(connection: Connection) -> tuple[MedicalRecord, ...]:
    """Повертає всі медичні записи з розрахованими статусами.
    Возвращает все медицинские записи с рассчитанными статусами.
    """

    rows = connection.execute(
        """
        SELECT
            medical_records.id,
            medical_records.employee_personnel_number,
            employees.full_name,
            medical_records.valid_from,
            medical_records.valid_until,
            medical_records.medical_decision,
            medical_records.restriction_note
        FROM medical_records
        INNER JOIN employees
            ON employees.personnel_number = medical_records.employee_personnel_number
        ORDER BY medical_records.valid_until ASC, medical_records.id ASC;
        """
    ).fetchall()

    records: list[MedicalRecord] = []
    for row in rows:
        medical_record = MedicalRecord(
            record_id=int(row["id"]),
            employee_personnel_number=row["employee_personnel_number"],
            employee_full_name=row["full_name"],
            valid_from=row["valid_from"],
            valid_until=row["valid_until"],
            medical_decision=MedicalDecision(row["medical_decision"]),
            restriction_note=row["restriction_note"] or "",
            status=MedicalStatus.CURRENT,
        )
        records.append(
            MedicalRecord(
                record_id=medical_record.record_id,
                employee_personnel_number=medical_record.employee_personnel_number,
                employee_full_name=medical_record.employee_full_name,
                valid_from=medical_record.valid_from,
                valid_until=medical_record.valid_until,
                medical_decision=medical_record.medical_decision,
                restriction_note=medical_record.restriction_note,
                status=evaluate_medical_status(medical_record),
            )
        )

    return tuple(records)
