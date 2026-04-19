from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label


# ###### ПОБУДОВА ЗВЕДЕННЯ УЧАСНИКІВ НАРЯДУ / ПОСТРОЕНИЕ СВОДКИ УЧАСТНИКОВ НАРЯДА ######
def build_work_permit_participants_summary(work_permit_record: WorkPermitRecord) -> str:
    """Повертає короткий текстовий перелік учасників наряду-допуску.
    Возвращает краткий текстовый перечень участников наряда-допуска.
    """

    if not work_permit_record.participants:
        return "Учасники не задані"
    return ", ".join(
        f"{participant.employee_full_name} ({format_work_permit_participant_role_label(participant.participant_role)})"
        for participant in work_permit_record.participants
    )
