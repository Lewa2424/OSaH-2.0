from dataclasses import dataclass

from osah.domain.entities.app_section import AppSection


@dataclass(slots=True)
class AiNavigationTarget:
    """Ціль навігації, зібрана з AI-intent без Qt-залежностей.
    Navigation target built from an AI intent without Qt dependencies.
    """

    section: AppSection
    employee_personnel_number: str | None = None
    ppe_status_filter: str | None = None
    training_status_filter: str | None = None
    medical_status_filter: str | None = None
    work_permit_status_filter: str | None = None
