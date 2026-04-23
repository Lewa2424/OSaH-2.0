from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.domain.entities.notification_item import NotificationItem
from osah.ui.qt.components.alert_card import AlertCard
from osah.ui.qt.components.metric_card import MetricCard
from osah.ui.qt.components.screen_states import EmptyStateWidget
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import COLOR, SPACING


class DashboardScreen(QWidget):
    """Dashboard as a unified control panel screen."""

    employee_attention_requested = Signal(str, str)
    trainings_attention_requested = Signal(str)
    ppe_attention_requested = Signal(str)
    medical_attention_requested = Signal(str)
    work_permits_attention_requested = Signal(str)

    def __init__(self, snapshot: DashboardSnapshot, service_audit_entries: tuple[AuditLogEntry, ...] = ()) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(
            SectionHeader(
                "Головна",
                "Дашборд-пульт: критичні сигнали, проблемні контури, швидкі переходи та службовий стан системи.",
            )
        )

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(SPACING["lg"])
        metrics_layout.addWidget(
            MetricCard(
                title="Працівники",
                value=str(snapshot.employee_total),
                subtitle="Контур персоналу",
                accent_color=COLOR["accent"],
            )
        )
        metrics_layout.addWidget(
            MetricCard(
                title="Критичні проблеми",
                value=str(snapshot.critical_items),
                subtitle="Недопуски і прострочки",
                accent_color=COLOR["critical"],
            )
        )
        metrics_layout.addWidget(
            MetricCard(
                title="Потребують уваги",
                value=str(snapshot.warning_items),
                subtitle="Порогові сигнали",
                accent_color=COLOR["warning"],
            )
        )
        metrics_layout.addWidget(
            MetricCard(
                title="Нові матеріали",
                value=str(snapshot.unread_news_total),
                subtitle="НПА/новини",
                accent_color=COLOR["news_accent"],
            )
        )
        layout.addLayout(metrics_layout)

        sections_layout = QHBoxLayout()
        sections_layout.setSpacing(SPACING["lg"])
        sections_layout.addWidget(self._build_alerts_panel(snapshot), stretch=6)
        sections_layout.addWidget(self._build_focus_panel(snapshot, service_audit_entries), stretch=4)
        layout.addLayout(sections_layout)

    # ###### ПАНЕЛЬ СПОВІЩЕНЬ / ALERTS PANEL ######
    def _build_alerts_panel(self, snapshot: DashboardSnapshot) -> QWidget:
        """Builds active notifications panel."""

        panel = QWidget()
        panel.setProperty("inset", "true")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        title = QLabel("Активні сповіщення")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        if snapshot.active_notifications:
            for notification in snapshot.active_notifications[:6]:
                card = AlertCard(notification)
                card.clicked.connect(lambda item=notification: self._emit_employee_attention(item))
                layout.addWidget(card)
        else:
            empty_state = EmptyStateWidget()
            empty_state.show_state("Активних сповіщень немає.", "Система не бачить відкритих проблемних сигналів.")
            layout.addWidget(empty_state)

        layout.addStretch()
        return panel

    # ###### ПАНЕЛЬ ФОКУСУ / FOCUS PANEL ######
    def _build_focus_panel(self, snapshot: DashboardSnapshot, service_audit_entries: tuple[AuditLogEntry, ...]) -> QWidget:
        """Builds quick actions, news and service state panel."""

        panel = QWidget()
        panel.setProperty("inset", "true")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        focus_title = QLabel("Фокус дня")
        focus_title.setProperty("role", "section_title")
        layout.addWidget(focus_title)

        training_critical, training_warning = _count_training_notifications(snapshot)
        ppe_critical, ppe_warning = _count_ppe_notifications(snapshot)
        medical_critical, medical_warning = _count_medical_notifications(snapshot)
        permit_critical, permit_warning = _count_work_permit_notifications(snapshot)

        layout.addWidget(_focus_line("Інструктажі", training_critical, training_warning))
        button = QPushButton("Відкрити проблемні інструктажі")
        button.setProperty("variant", "secondary")
        button.clicked.connect(
            lambda: self.trainings_attention_requested.emit("missing" if training_critical else "warning")
        )
        layout.addWidget(button)

        layout.addWidget(_focus_line("ЗІЗ", ppe_critical, ppe_warning))
        button = QPushButton("Відкрити проблемні ЗІЗ")
        button.setProperty("variant", "secondary")
        button.clicked.connect(lambda: self.ppe_attention_requested.emit("not_issued" if ppe_critical else "warning"))
        layout.addWidget(button)

        layout.addWidget(_focus_line("Медицина", medical_critical, medical_warning))
        button = QPushButton("Відкрити проблемну медицину")
        button.setProperty("variant", "secondary")
        button.clicked.connect(lambda: self.medical_attention_requested.emit("expired" if medical_critical else "warning"))
        layout.addWidget(button)

        layout.addWidget(_focus_line("Наряди-допуски", permit_critical, permit_warning))
        button = QPushButton("Відкрити проблемні наряди-допуски")
        button.setProperty("variant", "secondary")
        button.clicked.connect(
            lambda: self.work_permits_attention_requested.emit("expired" if permit_critical else "warning")
        )
        layout.addWidget(button)

        news_title = QLabel("Новини / НПА")
        news_title.setProperty("role", "section_title")
        layout.addWidget(news_title)
        if snapshot.latest_news_items:
            for news_item in snapshot.latest_news_items[:3]:
                news_label = QLabel(
                    f"• {news_item.source_name} | {news_item.published_at_text or '-'}\n{news_item.title_text}"
                )
                news_label.setProperty("role", "section_header_subtitle")
                news_label.setWordWrap(True)
                layout.addWidget(news_label)
        else:
            empty_news = EmptyStateWidget()
            empty_news.show_state("Нових матеріалів немає.", "Після перевірки джерел тут з'являться оновлення.")
            layout.addWidget(empty_news)

        service_title = QLabel("Службовий контроль")
        service_title.setProperty("role", "section_title")
        layout.addWidget(service_title)
        for service_status_text in _build_service_status_lines(service_audit_entries):
            service_label = QLabel(service_status_text)
            service_label.setProperty("role", "section_header_subtitle")
            service_label.setWordWrap(True)
            layout.addWidget(service_label)

        layout.addStretch()
        return panel

    # ###### ПЕРЕХІД ДО ПРАЦІВНИКА / EMPLOYEE ATTENTION NAVIGATION ######
    def _emit_employee_attention(self, notification: NotificationItem) -> None:
        """Emits request to open employee card and problem context."""

        if notification.employee_personnel_number:
            self.employee_attention_requested.emit(
                notification.employee_personnel_number,
                notification.source_module,
            )


# ###### РЯДОК ФОКУСУ КОНТУРУ / FOCUS LINE ######
def _focus_line(module_title: str, critical_count: int, warning_count: int) -> QLabel:
    """Builds one summary line for module focus counters."""

    label = QLabel(f"{module_title}: критично {critical_count}, увага {warning_count}")
    label.setProperty("role", "section_header_subtitle")
    return label


# ###### ПІДРАХУНОК СИГНАЛІВ ІНСТРУКТАЖІВ / COUNT TRAINING SIGNALS ######
def _count_training_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Counts critical and warning notifications for trainings module."""

    critical = 0
    warning = 0
    for notification in snapshot.active_notifications:
        if not notification.source_module.startswith("trainings."):
            continue
        if notification.notification_level.value == "critical":
            critical += 1
        elif notification.notification_level.value == "warning":
            warning += 1
    return critical, warning


# ###### ПІДРАХУНОК СИГНАЛІВ ЗІЗ / COUNT PPE SIGNALS ######
def _count_ppe_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Counts critical and warning notifications for PPE module."""

    critical = 0
    warning = 0
    for notification in snapshot.active_notifications:
        if not notification.source_module.startswith("ppe."):
            continue
        if notification.notification_level.value == "critical":
            critical += 1
        elif notification.notification_level.value == "warning":
            warning += 1
    return critical, warning


# ###### ПІДРАХУНОК СИГНАЛІВ МЕДИЦИНИ / COUNT MEDICAL SIGNALS ######
def _count_medical_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Counts critical and warning notifications for medical module."""

    critical = 0
    warning = 0
    for notification in snapshot.active_notifications:
        if not notification.source_module.startswith("medical."):
            continue
        if notification.notification_level.value == "critical":
            critical += 1
        elif notification.notification_level.value == "warning":
            warning += 1
    return critical, warning


# ###### ПІДРАХУНОК СИГНАЛІВ НАРЯДІВ / COUNT WORK PERMIT SIGNALS ######
def _count_work_permit_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Counts critical and warning notifications for work permit module."""

    critical = 0
    warning = 0
    for notification in snapshot.active_notifications:
        if not notification.source_module.startswith("work_permits."):
            continue
        if notification.notification_level.value == "critical":
            critical += 1
        elif notification.notification_level.value == "warning":
            warning += 1
    return critical, warning


# ###### СЛУЖБОВІ СТАТУСИ ЗОВНІШНЬОГО КОНТУРУ / EXTERNAL SERVICE STATUS LINES ######
def _build_service_status_lines(audit_entries: tuple[AuditLogEntry, ...]) -> tuple[str, ...]:
    """Builds short status lines for mail and NPA sources."""

    latest_mail = _find_latest_entry(audit_entries, "reports_mail")
    latest_news = _find_latest_entry(audit_entries, "news_npa")
    return (
        _format_service_line("Пошта", latest_mail),
        _format_service_line("Джерела НПА", latest_news),
    )


# ###### ОСТАННЯ ПОДІЯ МОДУЛЯ / LATEST MODULE EVENT ######
def _find_latest_entry(audit_entries: tuple[AuditLogEntry, ...], module_name: str) -> AuditLogEntry | None:
    """Returns latest audit event for requested module."""

    for audit_entry in audit_entries:
        if audit_entry.module_name == module_name:
            return audit_entry
    return None


# ###### ФОРМАТ СЛУЖБОВОГО РЯДКА / SERVICE LINE FORMAT ######
def _format_service_line(title: str, audit_entry: AuditLogEntry | None) -> str:
    """Formats audit event into readable service line."""

    if audit_entry is None:
        return f"{title}: подій ще немає"
    return f"{title}: {audit_entry.result_status} | {audit_entry.event_type} | {audit_entry.created_at_text}"
