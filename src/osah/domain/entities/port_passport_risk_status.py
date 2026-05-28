from enum import StrEnum


class PortPassportRiskStatus(StrEnum):
    """Статус ризику в межах конкретного паспорта ділянки.
    Risk status within a specific site passport.
    """

    SUGGESTED = "suggested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MANUAL = "manual"


PORT_PASSPORT_RISK_STATUS_LABELS: dict[PortPassportRiskStatus, str] = {
    PortPassportRiskStatus.SUGGESTED: "Запропонований",
    PortPassportRiskStatus.ACCEPTED: "Прийнятий",
    PortPassportRiskStatus.REJECTED: "Відхилений",
    PortPassportRiskStatus.MANUAL: "Доданий вручну",
}


def format_port_passport_risk_status(status: PortPassportRiskStatus) -> str:
    """Повертає український UI-напис статусу ризику.
    Returns the Ukrainian UI label for a risk status.
    """

    return PORT_PASSPORT_RISK_STATUS_LABELS[status]
