from osah.domain.entities.work_permit_status import WorkPermitStatus


def format_work_permit_status_label(work_permit_status: WorkPermitStatus) -> str:
    """Повертає коротку українську мітку статусу наряду-допуску.
    Returns a short Ukrainian label for a work permit status.
    """

    labels = {
        WorkPermitStatus.ACTIVE: "Діє",
        WorkPermitStatus.WARNING: "Скоро спливає",
        WorkPermitStatus.EXPIRED: "Прострочено",
        WorkPermitStatus.CLOSED: "Закрито",
        WorkPermitStatus.CANCELED: "Скасовано",
        WorkPermitStatus.REISSUED: "Скасовано",
        WorkPermitStatus.INVALID: "Проблемний",
    }
    return labels[work_permit_status]
