from osah.domain.entities.work_permit_record import WorkPermitRecord


# ###### СЕРІАЛІЗАЦІЯ НАРЯДУ ДЛЯ AUDIT / СЕРИАЛИЗАЦИЯ НАРЯДА ДЛЯ AUDIT ######
def serialize_work_permit_record_for_audit(work_permit_record: WorkPermitRecord) -> str:
    """Повертає короткий текстовий зліпок наряду-допуску для audit-події.
    Возвращает короткий текстовый слепок наряда-допуска для audit-события.
    """

    participants_text = ",".join(
        f"{participant.employee_personnel_number}:{participant.participant_role.value}"
        for participant in work_permit_record.participants
    )
    return (
        f"permit_number={work_permit_record.permit_number};"
        f"work_kind={work_permit_record.work_kind};"
        f"starts_at={work_permit_record.starts_at};"
        f"ends_at={work_permit_record.ends_at};"
        f"closed_at={work_permit_record.closed_at or ''};"
        f"participants={participants_text}"
    )
