from dataclasses import dataclass

from osah.domain.entities.ppe_status import PpeStatus


@dataclass(slots=True)
class PpeRecord:
    """Запис по засобу індивідуального захисту.
    Запись по средству индивидуальной защиты.
    """

    record_id: int | None
    employee_personnel_number: str
    employee_full_name: str
    ppe_name: str
    is_required: bool
    is_issued: bool
    issue_date: str
    replacement_date: str
    quantity: int
    note_text: str
    status: PpeStatus
