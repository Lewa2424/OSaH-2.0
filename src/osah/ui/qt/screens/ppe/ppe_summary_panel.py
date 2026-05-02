from osah.domain.entities.ppe_workspace_summary import PpeWorkspaceSummary
from osah.ui.qt.components.summary_strip import SummaryStrip
from osah.ui.qt.design.tokens import COLOR


class PpeSummaryPanel(SummaryStrip):
    """Швидкі показники модуля ЗІЗ.
    Quick metrics for the PPE module.
    """

    def __init__(self, summary: PpeWorkspaceSummary) -> None:
        super().__init__(
            (
                ("Усього", summary.total_rows, COLOR["accent"]),
                ("Критично", summary.critical_total + summary.not_issued_total, COLOR["critical"]),
                ("Увага", summary.warning_total, COLOR["warning"]),
                ("Актуально", summary.current_total, COLOR["success"]),
            )
        )

    # ###### ОНОВЛЕННЯ ПІДСУМКУ / UPDATE SUMMARY ######
    def set_summary(self, summary: PpeWorkspaceSummary) -> None:
        """Оновлює числа quick stats після зміни даних.
        Updates quick-stats values after data changes.
        """

        self.set_values(
            (
                summary.total_rows,
                summary.critical_total + summary.not_issued_total,
                summary.warning_total,
                summary.current_total,
            )
        )
