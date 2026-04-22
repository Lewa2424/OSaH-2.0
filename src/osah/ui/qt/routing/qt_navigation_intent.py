from dataclasses import dataclass

from osah.domain.entities.app_section import AppSection


@dataclass(slots=True)
class QtNavigationIntent:
    """Намір навігації між Qt-екранами без прихованої UI-логіки.
    Navigation intent between Qt screens without hidden UI logic.
    """

    target_section: AppSection
    employee_personnel_number: str | None = None
    problem_key: str | None = None
    training_status_filter: str | None = None
    ppe_status_filter: str | None = None
