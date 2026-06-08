from enum import StrEnum


ZONE_GREEN_MAX: float = 1.40
ZONE_YELLOW_MAX: float = 1.80


class PortShiftZone(StrEnum):
    """Кольорова зона динамічного ризику зміни (контур майстра ПОРТ-Р).
    Colour zone of the shift dynamic risk (PORT-R master circuit).
    """

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


PORT_SHIFT_ZONE_LABELS: dict[PortShiftZone, str] = {
    PortShiftZone.GREEN: "Зелена — продовжити",
    PortShiftZone.YELLOW: "Жовта — обмежити / бар'єр",
    PortShiftZone.RED: "Червона — СТОП",
}


def format_port_shift_zone(zone: PortShiftZone) -> str:
    """Повертає короткий україномовний напис зони ризику.
    Returns the short Ukrainian label for a risk zone.
    """

    return PORT_SHIFT_ZONE_LABELS[zone]


def zone_from_r_dyn(r_dyn: float) -> PortShiftZone:
    """Визначає зону ризику за числовим значенням R_dyn.
    Determines the risk zone from a numeric R_dyn value.
    """

    if r_dyn <= ZONE_GREEN_MAX:
        return PortShiftZone.GREEN
    if r_dyn <= ZONE_YELLOW_MAX:
        return PortShiftZone.YELLOW
    return PortShiftZone.RED
