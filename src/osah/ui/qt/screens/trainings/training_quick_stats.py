from osah.domain.entities.training_workspace_summary import TrainingWorkspaceSummary
from osah.ui.qt.components.summary_strip import SummaryStrip
from osah.ui.qt.design.tokens import COLOR


class TrainingQuickStats(SummaryStrip):
    """Швидкі показники модуля інструктажів.
    Quick metrics for the trainings module.
    """

    def __init__(self, summary: TrainingWorkspaceSummary) -> None:
        super().__init__(
            (
                ("Усього", summary.total_rows, COLOR["accent"]),
                ("Критично", summary.critical_total + summary.missing_total, COLOR["critical"]),
                ("Увага", summary.warning_total, COLOR["warning"]),
                ("Актуально", summary.current_total, COLOR["success"]),
            )
        )

    # ###### ОНОВЛЕННЯ МЕТРИК / UPDATE METRICS ######
    def set_summary(self, summary: TrainingWorkspaceSummary) -> None:
        """Оновлює числа quick stats після зміни даних.
        Updates quick-stats values after data changes.
        """

        self.set_values(
            (
                summary.total_rows,
                summary.critical_total + summary.missing_total,
                summary.warning_total,
                summary.current_total,
            )
        )
