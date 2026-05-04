from osah.domain.entities.ppe_record import PpeRecord


# ###### СЕРИАЛИЗАЦИЯ СИЗ ДЛЯ AUDIT / SERIALIZE PPE FOR AUDIT ######
def serialize_ppe_record_for_audit(ppe_record: PpeRecord) -> str:
    """Возвращает компактный текстовый слепок записи СИЗ для audit.
    Returns a compact textual snapshot of a PPE record for audit.
    """

    return (
        f"id={ppe_record.record_id}; employee={ppe_record.employee_personnel_number}; "
        f"ppe={ppe_record.ppe_name}; required={ppe_record.is_required}; issued={ppe_record.is_issued}; "
        f"issue_date={ppe_record.issue_date}; replacement={ppe_record.replacement_date}; "
        f"quantity={ppe_record.quantity}; provision={ppe_record.provision_status.value}; "
        f"compliance={ppe_record.compliance_check_state.value}; "
        f"basis_text={ppe_record.basis_text}; basis_note={ppe_record.basis_note}; "
        f"note={ppe_record.note_text}"
    )
