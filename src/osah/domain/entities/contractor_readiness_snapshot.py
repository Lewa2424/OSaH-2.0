from dataclasses import dataclass

from osah.domain.entities.contractor_readiness_status import ContractorReadinessStatus


@dataclass(slots=True)
class ContractorReadinessSnapshot:
    """Зріз готовності підрядника для реєстру та картки.
    Contractor readiness snapshot for registry and details pane.
    """

    status: ContractorReadinessStatus
    status_label: str
    can_work_now: bool
    total_workers: int
    ready_workers: int
    problem_workers: int
    headline_text: str
    issues_text: str
