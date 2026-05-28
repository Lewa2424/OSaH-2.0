from enum import StrEnum


class PortRiskProfile(StrEnum):
    """Профіль ризику паспорта ділянки.
    Risk profile of a site passport.
    """

    NOT_CALCULATED = "not_calculated"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


PORT_RISK_PROFILE_LABELS: dict[PortRiskProfile, str] = {
    PortRiskProfile.NOT_CALCULATED: "Не розраховано",
    PortRiskProfile.LOW: "Низький",
    PortRiskProfile.MEDIUM: "Середній",
    PortRiskProfile.HIGH: "Високий",
    PortRiskProfile.CRITICAL: "Критичний",
}


def format_port_risk_profile(profile: PortRiskProfile) -> str:
    """Повертає український UI-напис профілю ризику.
    Returns the Ukrainian UI label for a risk profile.
    """

    return PORT_RISK_PROFILE_LABELS[profile]
