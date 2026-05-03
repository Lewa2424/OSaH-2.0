"""
TopCommandBar — верхня панель команд.
Відображає назву поточного розділу, контекст та іконки керування.
TopCommandBar — top command bar showing section title and contextual controls.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee_topbar_summary import EmployeeTopbarSummary
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.security.format_access_role_label import format_access_role_label
from osah.ui.qt.design.tokens import COLOR, FONT, SPACING


class TopCommandBar(QWidget):
    """Верхня панель інструментів (Top bar).
    Top toolbar component containing section title and global controls.
    """

    def __init__(self, access_role: AccessRole) -> None:
        super().__init__()
        self.setProperty("role", "topbar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(84)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(SPACING["xl"], SPACING["sm"], SPACING["xl"], SPACING["sm"])
        self._layout.setSpacing(SPACING["lg"])

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        self._default_title_font = QFont(FONT["title_xl"][0], FONT["title_xl"][1])
        self._default_title_font.setBold(FONT["title_xl"][2])
        self._composed_title_font = QFont(FONT["title_xl"][0], 20)
        self._composed_title_font.setBold(True)

        self._title_label = QLabel()
        self._title_label.setProperty("role", "title")
        self._title_label.setFont(self._default_title_font)
        self._title_label.setTextFormat(Qt.TextFormat.RichText)
        text_layout.addWidget(self._title_label)

        self._subtitle_label = QLabel()
        self._subtitle_label.setProperty("role", "subtitle")
        text_layout.addWidget(self._subtitle_label)

        self._layout.addLayout(text_layout)

        self._kpi_panel = QWidget()
        self._kpi_layout = QHBoxLayout(self._kpi_panel)
        self._kpi_layout.setContentsMargins(0, 0, 0, 0)
        self._kpi_layout.setSpacing(SPACING["md"])
        self._kpi_panel.hide()
        self._layout.addWidget(self._kpi_panel, 3)
        self._layout.addStretch()

        self._role_label = QLabel(f"Роль: {format_access_role_label(access_role)}")
        self._role_label.setStyleSheet(
            f"background: {COLOR['role_tag_bg']}; "
            f"color: {COLOR['role_tag_text']}; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: 14px; "
            f"padding: 9px 18px; "
            f"font-weight: 800; "
            f"font-size: 13px;"
        )
        self._layout.addWidget(self._role_label)
        self._layout.setAlignment(self._role_label, Qt.AlignmentFlag.AlignVCenter)

    def set_section(self, section: AppSection, alert_level: NotificationLevel | None = None) -> None:
        """Оновлює заголовок відповідно до вибраного розділу."""

        self._title_label.setFont(self._composed_title_font)
        self._title_label.show()
        self._subtitle_label.hide()
        self._clear_kpis()
        self._kpi_panel.hide()

        descriptions = {
            AppSection.DASHBOARD: "огляд сигналів і стану системи",
            AppSection.EMPLOYEES: "реєстр персоналу, фільтри та картка працівника",
            AppSection.TRAININGS: "облік проведення, строків повторення та проблемних записів",
            AppSection.PPE: "норми, видача, строки заміни та критичні відхилення",
            AppSection.MEDICAL: "меддопуск, строки дії та робочі обмеження",
            AppSection.WORK_PERMITS: "активні, прострочені та проблемні допуски до робіт",
            AppSection.CONTRACTORS: "облік підрядників і контроль їхнього допуску",
            AppSection.ARCHIVE: "архів подій, записів і службових підстав",
            AppSection.REPORTS: "щоденний звіт, доставка та службові помилки",
            AppSection.NEWS_NPA: "довірені джерела НПА та новин",
            AppSection.SETTINGS: "резервні копії, імпорт, журнал і параметри системи",
            AppSection.ABOUT: "версія, склад системи та технічний контекст",
        }
        description_text = descriptions.get(section, "керування розділом")
        self._title_label.setText(
            f"<span style='font-size:20pt; font-weight:700;'>{section.value}</span> "
            f"<span style='font-size:16pt; font-weight:400;'>({description_text})</span>"
        )

    def set_employee_summary(self, summary: EmployeeTopbarSummary) -> None:
        """Оновлює topbar кадровими KPI.
        Updates topbar with employee KPIs.
        """

        self._title_label.hide()
        self._subtitle_label.hide()
        self._clear_kpis()
        self._kpi_layout.addWidget(_build_kpi_chip("Працівники", str(summary.active_employee_count)), 1)
        self._kpi_layout.addWidget(_build_kpi_chip("Підрозділи", str(summary.department_count)), 1)
        self._kpi_layout.addWidget(_build_kpi_chip("Нові 14 днів", str(summary.new_employee_count)), 1)
        self._kpi_layout.addWidget(_build_kpi_chip("Архів", str(summary.archived_employee_count)), 1)
        self._kpi_panel.show()

    def _clear_kpis(self) -> None:
        """Очищує KPI-чіпи topbar.
        Clears topbar KPI chips.
        """

        while self._kpi_layout.count():
            item = self._kpi_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()


# ###### KPI-ЧІП ВЕРХНЬОЇ ПАНЕЛІ / TOPBAR KPI CHIP ######
def _build_kpi_chip(title: str, value: str) -> QFrame:
    """Створює компактний KPI-чіп для верхньої панелі.
    Creates a compact KPI chip for the top command bar.
    """

    chip = QFrame()
    chip.setObjectName("topbarKpiChip")
    chip.setStyleSheet(
        f"QFrame#topbarKpiChip {{ "
        f"background: {COLOR['bg_card']}; "
        f"border: 1px solid {COLOR['border_soft']}; "
        f"border-radius: 12px; "
        f"}}"
    )
    layout = QVBoxLayout(chip)
    layout.setContentsMargins(18, 8, 18, 8)
    layout.setSpacing(2)

    title_label = QLabel(title)
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
    title_label.setStyleSheet(f"color: {COLOR['text_secondary']};")
    layout.addWidget(title_label)

    value_label = QLabel(value)
    value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
    value_label.setStyleSheet(f"color: {COLOR['accent']};")
    layout.addWidget(value_label)

    return chip
