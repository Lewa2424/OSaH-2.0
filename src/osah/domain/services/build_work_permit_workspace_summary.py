from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.entities.work_permit_workspace_summary import WorkPermitWorkspaceSummary


# ###### ПІДСУМОК НАРЯДІВ / WORK PERMIT SUMMARY ######
def build_work_permit_workspace_summary(rows: tuple[WorkPermitWorkspaceRow, ...]) -> WorkPermitWorkspaceSummary:
    """Рахує короткі показники модуля нарядів-допусків.
    Counts compact indicators for the work permits module.
    """

    active_statuses = {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING, WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID}
    return WorkPermitWorkspaceSummary(
        total_rows=len(rows),
        active_total=sum(1 for row in rows if row.status == WorkPermitStatus.ACTIVE),
        warning_total=sum(1 for row in rows if row.status == WorkPermitStatus.WARNING),
        expired_total=sum(1 for row in rows if row.status in {WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID}),
        closed_total=sum(1 for row in rows if row.status == WorkPermitStatus.CLOSED),
        canceled_total=sum(1 for row in rows if row.status == WorkPermitStatus.CANCELED),
        conflict_total=sum(1 for row in rows if row.has_conflicts),
        active_participants_total=sum(row.participant_count for row in rows if row.status in active_statuses),
    )
