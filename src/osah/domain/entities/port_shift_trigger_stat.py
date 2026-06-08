from dataclasses import dataclass

from osah.domain.entities.port_macrovariable import PortMacrovariable


@dataclass(slots=True)
class PortShiftTriggerStat:
    """Агрегат повторюваності одного тригера у журналі змін ПОРТ-Р за період.
    Aggregated recurrence of a single trigger in the PORT-R shift log over a period.
    """

    passport_id: int
    passport_code: str
    site_name: str
    macrovariable: PortMacrovariable
    threshold_id: int
    trigger_text: str
    is_stop_trigger: bool
    hit_count: int
    last_shift_date: str
