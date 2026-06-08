from dataclasses import dataclass

from osah.domain.entities.port_macrovariable import PortMacrovariable


@dataclass(slots=True)
class PortMacrovariableThreshold:
    """Тригер відхилення для макрозмінної паспорта ПОРТ-Р (калібрування інженером).
    A deviation trigger for a PORT-R passport macrovariable (engineer calibration).
    """

    threshold_id: int
    passport_id: int
    macrovariable: PortMacrovariable
    trigger_text: str
    k_value: float
    is_stop_trigger: bool
