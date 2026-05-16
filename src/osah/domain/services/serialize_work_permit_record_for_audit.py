from osah.domain.entities.work_permit_record import WorkPermitRecord


# ###### РЎР•Р РРђР›РР—РђР¦РРЇ РќРђР РЇР”Рђ Р”Р›РЇ AUDIT / SERIALIZE WORK PERMIT FOR AUDIT ######
def serialize_work_permit_record_for_audit(work_permit_record: WorkPermitRecord) -> str:
    """Р’РѕР·РІСЂР°С‰Р°РµС‚ РєРѕСЂРѕС‚РєРёР№ С‚РµРєСЃС‚РѕРІС‹Р№ СЃР»РµРїРѕРє РЅР°СЂСЏРґР°-РґРѕРїСѓСЃРєР° РґР»СЏ audit-СЃРѕР±С‹С‚РёСЏ.
    Returns a compact textual snapshot of a work permit for audit events.
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
        f"base_ends_at={work_permit_record.base_ends_at};"
        f"extension_count={work_permit_record.extension_count};"
        f"extended_at={work_permit_record.extended_at or ''};"
        f"extension_reason_text={work_permit_record.extension_reason_text};"
        f"closed_at={work_permit_record.closed_at or ''};"
        f"canceled_at={work_permit_record.canceled_at or ''};"
        f"reissued_from_record_id={work_permit_record.reissued_from_record_id or ''};"
        f"reissued_to_record_id={work_permit_record.reissued_to_record_id or ''};"
        f"reissue_reason_text={work_permit_record.reissue_reason_text};"
        f"target_training_status={work_permit_record.target_training_status.value};"
        f"target_training_date={work_permit_record.target_training_date};"
        f"target_training_by={work_permit_record.target_training_conducted_by};"
        f"target_training_note={work_permit_record.target_training_note};"
        f"basis_text={work_permit_record.basis_text};"
        f"basis_note={work_permit_record.basis_note};"
        f"daily_check_count={len(work_permit_record.daily_checks)};"
        f"participants={participants_text}"
    )
