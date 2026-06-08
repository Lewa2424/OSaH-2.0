from enum import StrEnum


class PortShiftDecision(StrEnum):
    """Управлінське рішення за підсумком оцінки зміни ПОРТ-Р.
    Management decision resulting from a PORT-R shift assessment.
    """

    CONTINUE = "continue"
    RESTRICT = "restrict"
    STOP = "stop"


PORT_SHIFT_DECISION_LABELS: dict[PortShiftDecision, str] = {
    PortShiftDecision.CONTINUE: "Продовжити роботу",
    PortShiftDecision.RESTRICT: "Обмежити (з бар'єром)",
    PortShiftDecision.STOP: "СТОП — роботи припинено",
}


def format_port_shift_decision(decision: PortShiftDecision) -> str:
    """Повертає україномовний напис рішення зміни.
    Returns the Ukrainian label for a shift decision.
    """

    return PORT_SHIFT_DECISION_LABELS[decision]
