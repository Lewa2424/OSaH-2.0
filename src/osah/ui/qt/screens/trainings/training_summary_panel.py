from PySide6.QtWidgets import QFrame, QLabel, QGridLayout, QVBoxLayout, QWidget

from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.format_training_next_control_basis_label import format_training_next_control_basis_label
from osah.domain.services.format_training_work_risk_category_label import format_training_work_risk_category_label
from osah.domain.services.format_ui_date import format_ui_date
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

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        outer.setSpacing(SPACING["md"])

        self._headline = QLabel("Контекст")
        self._headline.setStyleSheet("font-size: 16px; font-weight: 900;")
        outer.addWidget(self._headline)

        content = QWidget()
        grid = QGridLayout(content)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(SPACING["xl"])
        grid.setVerticalSpacing(SPACING["xs"])
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

        self._left_title = QLabel("Запис не вибрано")
        self._left_title.setStyleSheet("font-weight: 800;")
        self._left_meta = QLabel("Оберіть рядок у таблиці, щоб побачити деталі.")
        self._left_meta.setWordWrap(True)
        self._left_meta.setStyleSheet(f"color: {COLOR['text_secondary']};")
        self._left_dates = QLabel("")
        self._left_dates.setWordWrap(True)
        self._left_dates.setStyleSheet(f"color: {COLOR['text_secondary']};")

        self._right_reason = QLabel("Статус і службові деталі з'являться тут.")
        self._right_reason.setWordWrap(True)
        self._right_reason.setStyleSheet("font-weight: 700;")
        self._right_details = QLabel("")
        self._right_details.setWordWrap(True)
        self._right_details.setStyleSheet(f"color: {COLOR['text_secondary']};")

        grid.addWidget(self._left_title, 0, 0)
        grid.addWidget(self._right_reason, 0, 1)
        grid.addWidget(self._left_meta, 1, 0)
        grid.addWidget(self._right_details, 1, 1)
        grid.addWidget(self._left_dates, 2, 0)
        outer.addWidget(content)

    # ###### ОНОВЛЕННЯ ПІДСУМКУ / UPDATE SUMMARY ######
    def set_row(self, row: TrainingWorkspaceRow) -> None:
        """Оновлює панель пояснення за вибраним рядком.
        Updates explanation panel from the selected row.
        """

        self._headline.setText("Контекст інструктажу")
        self._left_title.setText(f"{row.employee_full_name} / {row.training_type_label}")
        self._left_meta.setText(
            f"{row.department_name}\n"
            f"{row.position_name}\n"
            f"Проводив: {row.conducted_by}"
        )
        self._left_dates.setText(
            f"Проведено: {format_ui_date(row.event_date)}\n"
            f"Наступний строк: {format_ui_date(row.next_control_date)}"
        )
        self._right_reason.setText(row.status_reason)
        self._right_details.setText(
            f"Категорія робіт: {format_training_work_risk_category_label(row.work_risk_category)}\n"
            f"Підстава дати: {format_training_next_control_basis_label(row.next_control_basis)}\n"
            f"Статус: {row.status_label}"
        )
