from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.entities.training_workspace_summary import TrainingWorkspaceSummary


# ###### ПІДСУМОК ІНСТРУКТАЖІВ / TRAININGS SUMMARY ######
def build_training_workspace_summary(rows: tuple[TrainingWorkspaceRow, ...]) -> TrainingWorkspaceSummary:
    """Рахує ключові показники робочого простору інструктажів.
    Counts key metrics for the trainings workspace.
    """

    return TrainingWorkspaceSummary(
        total_rows=len(rows),
        current_total=sum(1 for row in rows if row.status_filter == TrainingRegistryFilter.CURRENT),
        warning_total=sum(1 for row in rows if row.status_filter == TrainingRegistryFilter.WARNING),
        critical_total=sum(1 for row in rows if row.status_filter == TrainingRegistryFilter.OVERDUE),
        missing_total=sum(1 for row in rows if row.status_filter == TrainingRegistryFilter.MISSING),
    )
