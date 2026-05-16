from dataclasses import dataclass


@dataclass(slots=True)
class WorkPermitDailyCheck:
    """Щоденна перевірка місця виконання робіт за нарядом-допуском.
    Daily check of the work area for a work permit.
    """

    check_id: int | None
    checked_at: str
    checked_by: str
    note_text: str = ""
