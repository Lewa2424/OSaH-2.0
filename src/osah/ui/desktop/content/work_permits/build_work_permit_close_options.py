from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### ПОБУДОВА ОПЦІЙ ЗАКРИТТЯ НАРЯДУ / ПОСТРОЕНИЕ ОПЦИЙ ЗАКРЫТИЯ НАРЯДА ######
def build_work_permit_close_options(work_permit_records: tuple[WorkPermitRecord, ...]) -> tuple[str, ...]:
    """Повертає підписи нарядів-допусків, які ще можна закрити вручну.
    Возвращает подписи нарядов-допусков, которые ещё можно закрыть вручную.
    """

    return tuple(
        f"{work_permit_record.record_id} | {work_permit_record.permit_number} | {work_permit_record.work_kind}"
        for work_permit_record in work_permit_records
        if work_permit_record.status != WorkPermitStatus.CLOSED and work_permit_record.record_id is not None
    )
