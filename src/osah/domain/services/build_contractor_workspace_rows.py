from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_workspace_row import ContractorWorkspaceRow
from osah.domain.services.build_contractor_readiness_snapshot import build_contractor_readiness_snapshot


def build_contractor_workspace_rows(records: tuple[ContractorRecord, ...]) -> tuple[ContractorWorkspaceRow, ...]:
    """Готує рядки реєстру підрядників із підрахованою готовністю.
    Prepares contractor registry rows with computed readiness.
    """

    return tuple(
        ContractorWorkspaceRow(record=record, readiness=build_contractor_readiness_snapshot(record))
        for record in records
    )
