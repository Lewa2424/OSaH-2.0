from osah.domain.entities.work_permit_workspace_summary import WorkPermitWorkspaceSummary
from osah.ui.qt.components.summary_strip import SummaryStrip
from osah.ui.qt.design.tokens import COLOR


class WorkPermitSummaryPanel(SummaryStrip):
    """Швидкі показники модуля нарядів-допусків.
    Quick metrics for the work permits module.
    """

    def __init__(self, summary: WorkPermitWorkspaceSummary) -> None:
        super().__init__(
            (
                ("Діють", summary.active_total, COLOR["success"]),
                ("Скоро спливають", summary.warning_total, COLOR["warning"]),
                ("Критично", summary.expired_total, COLOR["critical"]),
                ("Конфлікти", summary.conflict_total, COLOR["critical"]),
                ("Учасники активних робіт", summary.active_participants_total, COLOR["accent"]),
            )
        )

    # ###### ОНОВЛЕННЯ ПІДСУМКУ / UPDATE SUMMARY ######
    def set_summary(self, summary: WorkPermitWorkspaceSummary) -> None:
        """Оновлює числа summary-strip після зміни даних.
        Updates summary-strip values after data changes.
        """

        self.set_values(
            (
                summary.active_total,
                summary.warning_total,
                summary.expired_total,
                summary.conflict_total,
                summary.active_participants_total,
            )
        )
