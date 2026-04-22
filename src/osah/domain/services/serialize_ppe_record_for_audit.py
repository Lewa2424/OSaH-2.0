from osah.domain.entities.ppe_record import PpeRecord


# ###### СЕРІАЛІЗАЦІЯ ЗІЗ ДЛЯ AUDIT / SERIALIZE PPE FOR AUDIT ######
def serialize_ppe_record_for_audit(ppe_record: PpeRecord) -> str:
    """Повертає компактний текстовий зліпок запису ЗІЗ для audit.
    Returns a compact textual snapshot of a PPE record for audit.
    """

    return (
        f"id={ppe_record.record_id}; employee={ppe_record.employee_personnel_number}; "
        f"ppe={ppe_record.ppe_name}; required={ppe_record.is_required}; issued={ppe_record.is_issued}; "
        f"issue_date={ppe_record.issue_date}; replacement={ppe_record.replacement_date}; "
        f"quantity={ppe_record.quantity}; note={ppe_record.note_text}"
    )
