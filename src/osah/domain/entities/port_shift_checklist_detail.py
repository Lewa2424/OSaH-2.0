from dataclasses import dataclass

from osah.domain.entities.port_macrovariable import PortMacrovariable
from osah.domain.entities.port_shift_checklist_row import PortShiftChecklistRow


@dataclass(slots=True)
class PortShiftTriggeredItem:
    """Один фактично спрацьований блок у конкретній оцінці зміни.
    A single actually-triggered block within a specific shift assessment.
    """

    macrovariable: PortMacrovariable
    threshold_id: int | None
    trigger_text: str
    k_used: float
    is_stop_trigger: bool


@dataclass(slots=True)
class PortShiftChecklistDetail:
    """Повна картка однієї оцінки зміни ПОРТ-Р: заголовок журналу + спрацьовані блоки.
    Full card of a single PORT-R shift assessment: log header + triggered blocks.
    """

    row: PortShiftChecklistRow
    triggered_items: tuple[PortShiftTriggeredItem, ...]
