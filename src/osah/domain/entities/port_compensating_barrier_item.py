from dataclasses import dataclass

from osah.domain.entities.port_macrovariable import PortMacrovariable


@dataclass(slots=True)
class PortCompensatingBarrierItem:
    """Компенсуючий бар'єр паспорта ПОРТ-Р зі знижувальним множником K_comp.
    A compensating barrier in a PORT-R passport with a reducing multiplier K_comp.
    """

    barrier_id: int
    passport_id: int
    barrier_name: str
    description: str
    k_comp: float
    macrovariable: PortMacrovariable = PortMacrovariable.B
