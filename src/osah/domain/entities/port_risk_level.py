from enum import StrEnum


class PortRiskLevel(StrEnum):
    """Рівень ризику для конкретного запису ризику в паспорті.
    Risk level for a specific risk record in a passport.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


PORT_RISK_LEVEL_LABELS: dict[PortRiskLevel, str] = {
    PortRiskLevel.LOW: "Низький",
    PortRiskLevel.MEDIUM: "Середній",
    PortRiskLevel.HIGH: "Високий",
    PortRiskLevel.CRITICAL: "Критичний",
}


def format_port_risk_level(level: PortRiskLevel) -> str:
    """Повертає Ukrainian UI-напис рівня ризику.
    Returns the Ukrainian UI label for a risk level.
    """
    return PORT_RISK_LEVEL_LABELS[level]
