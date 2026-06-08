from enum import StrEnum


class PortPassportStatus(StrEnum):
    """Статус життєвого циклу паспорта ділянки.
    Lifecycle status of a site passport.
    """

    DRAFT = "draft"
    NEEDS_RISK_ASSESSMENT = "needs_risk_assessment"
    NEEDS_ACTIONS = "needs_actions"
    ACTIVE = "active"
    REVISION = "revision"
    ARCHIVED = "archived"


PORT_PASSPORT_STATUS_LABELS: dict[PortPassportStatus, str] = {
    PortPassportStatus.DRAFT: "Чернетка",
    PortPassportStatus.NEEDS_RISK_ASSESSMENT: "Потребує оцінки",
    PortPassportStatus.NEEDS_ACTIONS: "Потребує заходів",
    PortPassportStatus.ACTIVE: "Діючий",
    PortPassportStatus.REVISION: "На перегляді",
    PortPassportStatus.ARCHIVED: "Архівний",
}


def format_port_passport_status(status: PortPassportStatus) -> str:
    """Повертає український UI-напис статусу паспорта.
    Returns the Ukrainian UI label for a passport status.
    """

    return PORT_PASSPORT_STATUS_LABELS[status]
