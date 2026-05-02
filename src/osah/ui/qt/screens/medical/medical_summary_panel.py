from osah.domain.entities.medical_workspace_summary import MedicalWorkspaceSummary
from osah.ui.qt.components.summary_strip import SummaryStrip
from osah.ui.qt.design.tokens import COLOR


class MedicalSummaryPanel(SummaryStrip):
    """Рядкові показники модуля медицини.
    Single-line metrics for the medical module.
    """

    def __init__(self, summary: MedicalWorkspaceSummary) -> None:
        super().__init__(
            (
                ("Усього", summary.total_rows, COLOR["accent"]),
                ("Не допущено", summary.critical_total, COLOR["critical"]),
                ("Обмежено", summary.restricted_total, COLOR["restricted"]),
                ("Увага", summary.warning_total, COLOR["warning"]),
                ("Допущено", summary.current_total, COLOR["success"]),
            )
        )

    # ###### ОНОВЛЕННЯ ПОКАЗНИКІВ / UPDATE METRICS ######
    def set_summary(self, summary: MedicalWorkspaceSummary) -> None:
        """Оновлює числа summary-strip після зміни даних.
        Updates summary-strip values after data changes.
        """

        self.set_values(
            (
                summary.total_rows,
                summary.critical_total,
                summary.restricted_total,
                summary.warning_total,
                summary.current_total,
            )
        )
