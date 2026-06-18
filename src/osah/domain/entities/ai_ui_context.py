from dataclasses import dataclass

from osah.domain.entities.app_section import AppSection


@dataclass(slots=True)
class AiUiContext:
    """Контекст поточного екрана для AI-команд.
    Current screen context snapshot for AI commands.
    """

    section: AppSection | None = None
    employee_personnel_number: str | None = None
    ppe_status_filter: str | None = None
    training_status_filter: str | None = None
    medical_status_filter: str | None = None
    work_permit_status_filter: str | None = None
    focused_field_key: str | None = None
    active_dialog: str | None = None
    permit_number: str | None = None
    port_passport_code: str | None = None
