from dataclasses import dataclass

from osah.domain.entities.port_shift_decision import PortShiftDecision
from osah.domain.entities.port_shift_zone import PortShiftZone


@dataclass(slots=True)
class PortShiftChecklistRow:
    """Рядок журналу відхилень зміни ПОРТ-Р (для таблиці в UI).
    A PORT-R shift deviation log row (for the UI table).
    """

    checklist_id: int
    passport_id: int
    passport_code: str
    site_name: str
    shift_date: str
    shift_label: str
    responsible_person: str
    r_base: float
    r_dyn: float | None
    zone: PortShiftZone | None
    decision: PortShiftDecision | None
    active_barrier_name: str
    stop_reason: str
    triggered_macrovariables: str
    created_at: str
