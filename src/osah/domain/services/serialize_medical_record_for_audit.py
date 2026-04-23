from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.services.format_medical_decision_label import format_medical_decision_label


# ###### СЕРІАЛІЗАЦІЯ МЕДИЦИНИ ДЛЯ AUDIT / SERIALIZE MEDICAL FOR AUDIT ######
def serialize_medical_record_for_audit(medical_record: MedicalRecord) -> str:
    """Повертає компактний текстовий зліпок медичного запису для audit.
    Returns a compact textual snapshot of a medical record for audit.
    """

    return (
        f"id={medical_record.record_id}; employee={medical_record.employee_personnel_number}; "
        f"valid_from={medical_record.valid_from}; valid_until={medical_record.valid_until}; "
        f"decision={format_medical_decision_label(medical_record.medical_decision)}; "
        f"restriction={medical_record.restriction_note}"
    )
