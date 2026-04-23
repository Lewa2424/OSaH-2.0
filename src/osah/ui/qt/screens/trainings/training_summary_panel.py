from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class TrainingSummaryPanel(QFrame):
    """Панель короткого пояснення вибраного стану інструктажу.
    Short explanation panel for selected training state.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("trainingSummaryPanel")
        self.setStyleSheet(
            f"QFrame#trainingSummaryPanel {{ "
            f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']};"
            f"border-radius: {RADIUS['lg']}px; "
            f"}}"
        )
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        self._title = QLabel("Контекст")
        self._title.setStyleSheet("font-weight: 900;")
        self._body = QLabel("Оберіть запис, щоб побачити причину статусу.")
        self._body.setWordWrap(True)
        self._body.setStyleSheet(f"color: {COLOR['text_secondary']};")
        self._layout.addWidget(self._title)
        self._layout.addWidget(self._body)

    # ###### ОНОВЛЕННЯ ПІДСУМКУ / UPDATE SUMMARY ######
    def set_row(self, row: TrainingWorkspaceRow) -> None:
        """Оновлює панель пояснення за вибраним рядком.
        Updates explanation panel from the selected row.
        """

        self._title.setText(f"{row.employee_full_name} / {row.training_type_label}")
        self._body.setText(row.status_reason)
