from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.format_training_next_control_basis_label import format_training_next_control_basis_label
from osah.domain.services.format_training_work_risk_category_label import format_training_work_risk_category_label
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class TrainingSummaryPanel(QFrame):
    """Short explanation panel for selected training state. / Панель пояснення стану інструктажу."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("trainingSummaryPanel")
        self.setStyleSheet(
            f"""
            QFrame#trainingSummaryPanel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255,255,255,0.98),
                    stop:1 rgba(241,246,251,0.98));
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xxl']}px;
            }}
            QLabel#summaryEyebrow {{
                color: {COLOR['accent']};
                font-size: 12px;
                font-weight: 900;
            }}
            QLabel#summaryHeadline {{
                color: {COLOR['text_primary']};
                font-size: 22px;
                font-weight: 900;
            }}
            QLabel#summaryBody {{
                color: {COLOR['text_secondary']};
                font-size: 15px;
                font-weight: 600;
            }}
            QLabel#summaryLead {{
                color: {COLOR['text_primary']};
                font-size: 16px;
                font-weight: 800;
            }}
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        outer.setSpacing(SPACING["md"])

        eyebrow = QLabel("КОНТУР ІНСТРУКТАЖІВ")
        eyebrow.setObjectName("summaryEyebrow")
        outer.addWidget(eyebrow)

        self._headline = QLabel("Контекст")
        self._headline.setObjectName("summaryHeadline")
        outer.addWidget(self._headline)

        content = QWidget()
        grid = QGridLayout(content)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(SPACING["xl"])
        grid.setVerticalSpacing(SPACING["sm"])
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

        self._left_title = QLabel("Запис не вибрано")
        self._left_title.setObjectName("summaryLead")
        self._left_meta = QLabel("Оберіть рядок у таблиці, щоб побачити деталі.")
        self._left_meta.setObjectName("summaryBody")
        self._left_meta.setWordWrap(True)
        self._left_dates = QLabel("")
        self._left_dates.setObjectName("summaryBody")
        self._left_dates.setWordWrap(True)

        self._right_reason = QLabel("Статус і службові деталі з'являться тут.")
        self._right_reason.setObjectName("summaryLead")
        self._right_reason.setWordWrap(True)
        self._right_details = QLabel("")
        self._right_details.setObjectName("summaryBody")
        self._right_details.setWordWrap(True)

        grid.addWidget(self._left_title, 0, 0)
        grid.addWidget(self._right_reason, 0, 1)
        grid.addWidget(self._left_meta, 1, 0)
        grid.addWidget(self._right_details, 1, 1)
        grid.addWidget(self._left_dates, 2, 0)
        outer.addWidget(content)

    def set_row(self, row: TrainingWorkspaceRow) -> None:
        self._headline.setText("Картка інструктажу")
        self._left_title.setText(f"{row.employee_full_name} / {row.training_type_label}")
        self._left_meta.setText(f"{row.department_name}\n{row.position_name}\nПроводив: {row.conducted_by}")
        self._left_dates.setText(
            f"Проведено: {format_ui_date(row.event_date)}\nНаступний строк: {format_ui_date(row.next_control_date)}"
        )
        self._right_reason.setText(row.status_reason)
        self._right_details.setText(
            f"Категорія робіт: {format_training_work_risk_category_label(row.work_risk_category)}\n"
            f"Підстава дати: {format_training_next_control_basis_label(row.next_control_basis)}\n"
            f"Статус: {row.status_label}"
        )
