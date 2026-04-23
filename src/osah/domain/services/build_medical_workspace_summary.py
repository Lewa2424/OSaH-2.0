from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.domain.entities.medical_workspace_summary import MedicalWorkspaceSummary


# ###### ПІДСУМОК МЕДИЦИНИ / MEDICAL SUMMARY ######
def build_medical_workspace_summary(rows: tuple[MedicalWorkspaceRow, ...]) -> MedicalWorkspaceSummary:
    """Рахує ключові показники робочого простору медицини.
    Counts key metrics for the medical workspace.
    """

    return MedicalWorkspaceSummary(
        total_rows=len(rows),
        current_total=sum(1 for row in rows if row.status == MedicalStatus.CURRENT),
        warning_total=sum(1 for row in rows if row.status == MedicalStatus.WARNING),
        restricted_total=sum(1 for row in rows if row.status == MedicalStatus.RESTRICTED),
        critical_total=sum(1 for row in rows if row.status in {MedicalStatus.EXPIRED, MedicalStatus.NOT_FIT}),
    )
