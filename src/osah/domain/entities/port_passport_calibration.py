from dataclasses import dataclass, field

from osah.domain.entities.port_compensating_barrier_item import PortCompensatingBarrierItem
from osah.domain.entities.port_macrovariable_threshold import PortMacrovariableThreshold


@dataclass(slots=True)
class PortPassportCalibration:
    """Калібрування динамічного контуру паспорта ПОРТ-Р: пороги Т-П-С-В-Б та компенсуючі бар'єри.
    Dynamic-circuit calibration for a PORT-R passport: T-P-S-V-B thresholds and compensating barriers.
    """

    passport_id: int
    r_base: float
    thresholds: tuple[PortMacrovariableThreshold, ...] = field(default_factory=tuple)
    compensating_barriers: tuple[PortCompensatingBarrierItem, ...] = field(default_factory=tuple)
