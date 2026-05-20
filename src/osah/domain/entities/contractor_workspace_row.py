from dataclasses import dataclass

from osah.domain.entities.contractor_readiness_snapshot import ContractorReadinessSnapshot
from osah.domain.entities.contractor_record import ContractorRecord


@dataclass(slots=True)
class ContractorWorkspaceRow:
    """Рядок реєстру підрядників із підрахованою готовністю.
    Contractors registry row with computed readiness.
    """

    record: ContractorRecord
    readiness: ContractorReadinessSnapshot
