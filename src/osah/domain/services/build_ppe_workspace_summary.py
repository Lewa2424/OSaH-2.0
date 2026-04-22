from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.entities.ppe_workspace_summary import PpeWorkspaceSummary


# ###### ПІДСУМОК ЗІЗ / PPE SUMMARY ######
def build_ppe_workspace_summary(rows: tuple[PpeWorkspaceRow, ...]) -> PpeWorkspaceSummary:
    """Рахує ключові показники робочого простору ЗІЗ.
    Counts key metrics for the PPE workspace.
    """

    return PpeWorkspaceSummary(
        total_rows=len(rows),
        current_total=sum(1 for row in rows if row.status == PpeStatus.CURRENT),
        warning_total=sum(1 for row in rows if row.status == PpeStatus.WARNING),
        critical_total=sum(1 for row in rows if row.status == PpeStatus.EXPIRED),
        not_issued_total=sum(1 for row in rows if row.status == PpeStatus.NOT_ISSUED),
    )
