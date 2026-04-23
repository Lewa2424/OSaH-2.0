"""
DashboardScreen — заглушка головного екрана нового UI.
Використовує MetricCard, InfoPanel та AlertCard для відображення даних з DashboardSnapshot.
DashboardScreen — dashboard stub using new UI components for DashboardSnapshot.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.domain.entities.notification_item import NotificationItem
from osah.ui.qt.components.alert_card import AlertCard
from osah.ui.qt.components.metric_card import MetricCard
from osah.ui.qt.design.tokens import COLOR, SIZE, SPACING


class DashboardScreen(QWidget):
    """Екран Dashboard у новій Qt архітектурі.
    Dashboard screen assembled with new architecture components.
    """

    employee_attention_requested = Signal(str, str)
    trainings_attention_requested = Signal(str)
    ppe_attention_requested = Signal(str)
    medical_attention_requested = Signal(str)
    work_permits_attention_requested = Signal(str)

    def __init__(self, snapshot: DashboardSnapshot, service_audit_entries: tuple[AuditLogEntry, ...] = ()) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xxl"], SPACING["xl"], SPACING["xxl"], SPACING["xl"])
        layout.setSpacing(SPACING["xl"])
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 0. Hero блок (Привітання і фокус)
        hero_layout = QHBoxLayout()
        hero_layout.setContentsMargins(0, 0, 0, SPACING["md"])
        
        greetings = QLabel("Доброго дня, інспектроре!")
        greetings.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR['text_primary']};")
        hero_layout.addWidget(greetings)
        hero_layout.addStretch()

        system_status = QLabel("Система: Нормальна робота")
        if snapshot.critical_items > 0:
            system_status.setText(f"Система: {snapshot.critical_items} критичних проблем!")
            system_status.setStyleSheet(f"color: {COLOR['critical']}; font-weight: bold; font-size: 14px;")
        elif snapshot.warning_items > 0:
            system_status.setText("Система: Потребує уваги")
            system_status.setStyleSheet(f"color: {COLOR['warning']}; font-weight: bold; font-size: 14px;")
        else:
            system_status.setStyleSheet(f"color: {COLOR['success']}; font-weight: bold; font-size: 14px;")

        hero_layout.addWidget(system_status)
        layout.addLayout(hero_layout)

        # 1. Верхній ряд: Метрики (Metrics row)
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
                subtitle="Підхід до порогу ризику",
                accent_color=COLOR["warning"],
            )
        )
        metrics_layout.addWidget(
            MetricCard(
                title="Нові матеріали",
                value=str(snapshot.unread_news_total),
                subtitle="Непрочитані новини",
                accent_color="#8B5CF6",  # Фіолетовий акцент
            )
        )

        layout.addLayout(metrics_layout)

        # 2. Нижній ряд: дві колонки
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(SPACING["xl"])

        # Ліва колонка: Алерт-фід (Left column: Alert feed)
        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(SPACING["md"])

        feed_title = QLabel("Активні сповіщення")
        feed_title.setProperty("role", "section_title")
        left_col.addWidget(feed_title)

        if snapshot.active_notifications:
            for n in snapshot.active_notifications[:5]:  # Показуємо топ-5
                card = AlertCard(n)
                card.clicked.connect(lambda notification=n: self._emit_employee_attention(notification))
                left_col.addWidget(card)
        else:
            empty_lbl = QLabel("Немає активних сповіщень. Все добре!")
            empty_lbl.setProperty("role", "empty_state")
            left_col.addWidget(empty_lbl)

        left_col.addStretch()
        left_wrap = QWidget()
        left_wrap.setLayout(left_col)
        cols_layout.addWidget(left_wrap, stretch=6)

        # Права колонка: Інфо-панель (Right column: Info/News)
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(SPACING["md"])

        info_title = QLabel("Швидкі дії та Фокус")
        info_title.setProperty("role", "section_title")
        right_col.addWidget(info_title)

        info_box = QWidget()
        info_box.setProperty("inset", "true")
        ib_layout = QVBoxLayout(info_box)
        ib_layout.setSpacing(SPACING["md"])
        
        from PySide6.QtWidgets import QPushButton

        training_critical, training_warning = _count_training_notifications(snapshot)
        ppe_critical, ppe_warning = _count_ppe_notifications(snapshot)
        medical_critical, medical_warning = _count_medical_notifications(snapshot)
        permit_critical, permit_warning = _count_work_permit_notifications(snapshot)
        training_status = QLabel(
            f"Інструктажі: критично {training_critical}, увага {training_warning}"
        )
        training_status.setStyleSheet(f"color: {COLOR['text_secondary']}; font-weight: 700;")
        ib_layout.addWidget(training_status)

        trainings_btn = QPushButton("Відкрити проблемні інструктажі")
        trainings_btn.setProperty("variant", "secondary")
        trainings_btn.clicked.connect(
            lambda: self.trainings_attention_requested.emit("missing" if training_critical else "warning")
        )
        ib_layout.addWidget(trainings_btn)

        ppe_status = QLabel(f"ЗІЗ: критично {ppe_critical}, увага {ppe_warning}")
        ppe_status.setStyleSheet(f"color: {COLOR['text_secondary']}; font-weight: 700;")
        ib_layout.addWidget(ppe_status)

        ppe_btn = QPushButton("Відкрити проблемні ЗІЗ")
        ppe_btn.setProperty("variant", "secondary")
        ppe_btn.clicked.connect(lambda: self.ppe_attention_requested.emit("not_issued" if ppe_critical else "warning"))
        ib_layout.addWidget(ppe_btn)

        medical_status = QLabel(f"Медицина: критично {medical_critical}, увага {medical_warning}")
        medical_status.setStyleSheet(f"color: {COLOR['text_secondary']}; font-weight: 700;")
        ib_layout.addWidget(medical_status)

        medical_btn = QPushButton("Відкрити проблемну медицину")
        medical_btn.setProperty("variant", "secondary")
        medical_btn.clicked.connect(lambda: self.medical_attention_requested.emit("expired" if medical_critical else "warning"))
        ib_layout.addWidget(medical_btn)
        
        permit_status = QLabel(f"Наряди-допуски: критично {permit_critical}, увага {permit_warning}")
        permit_status.setStyleSheet(f"color: {COLOR['text_secondary']}; font-weight: 700;")
        ib_layout.addWidget(permit_status)

        permit_btn = QPushButton("Відкрити проблемні наряди-допуски")
        permit_btn.setProperty("variant", "secondary")
        permit_btn.clicked.connect(lambda: self.work_permits_attention_requested.emit("expired" if permit_critical else "warning"))
        ib_layout.addWidget(permit_btn)
        
        btn2 = QPushButton("🛡️ Реєстрація інструктажу")
        btn2.setProperty("variant", "secondary")
        ib_layout.addWidget(btn2)
        
        ib_layout.addSpacing(SPACING["lg"])

        news_title = QLabel("Новини / НПА")
        news_title.setStyleSheet(f"color: {COLOR['text_primary']}; font-weight: 900;")
        ib_layout.addWidget(news_title)
        if snapshot.latest_news_items:
            for news_item in snapshot.latest_news_items[:3]:
                news_label = QLabel(
                    f"• {news_item.source_name} | {news_item.published_at_text or '-'}\n{news_item.title_text}"
                )
                news_label.setWordWrap(True)
                news_label.setStyleSheet(f"color: {COLOR['text_secondary']};")
                ib_layout.addWidget(news_label)
        else:
            news_empty = QLabel("Нових матеріалів із довірених джерел немає.")
            news_empty.setProperty("role", "status_muted")
            ib_layout.addWidget(news_empty)

        service_title = QLabel("Службовий контроль")
        service_title.setStyleSheet(f"color: {COLOR['text_primary']}; font-weight: 900;")
        ib_layout.addWidget(service_title)
        for service_status_text in _build_service_status_lines(service_audit_entries):
            status_label = QLabel(service_status_text)
            status_label.setWordWrap(True)
            status_label.setStyleSheet(f"color: {COLOR['text_secondary']};")
            ib_layout.addWidget(status_label)

        right_col.addWidget(info_box)
        right_col.addStretch()

        right_wrap = QWidget()
        right_wrap.setLayout(right_col)
        cols_layout.addWidget(right_wrap, stretch=4)

        layout.addLayout(cols_layout)

    # ###### ПЕРЕХІД ДО ПРАЦІВНИКА / EMPLOYEE ATTENTION NAVIGATION ######
    def _emit_employee_attention(self, notification: NotificationItem) -> None:
        """Передає запит перейти з Dashboard до працівника і контексту проблеми.
        Emits a request to navigate from Dashboard to an employee and problem context.
        """

        if notification.employee_personnel_number:
            self.employee_attention_requested.emit(
                notification.employee_personnel_number,
                notification.source_module,
            )


# ###### ПІДРАХУНОК СИГНАЛІВ ІНСТРУКТАЖІВ / COUNT TRAINING SIGNALS ######
def _count_training_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Рахує критичні та попереджувальні сповіщення модуля інструктажів.
    Counts critical and warning notifications for the trainings module.
    """

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


def _count_ppe_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Рахує критичні та попереджувальні сповіщення модуля ЗІЗ.
    Counts critical and warning notifications for the PPE module.
    """

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
    """Рахує критичні та попереджувальні сповіщення модуля медицини.
    Counts critical and warning notifications for the medical module.
    """

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
    """Рахує критичні та попереджувальні сповіщення модуля нарядів-допусків.
    Counts critical and warning notifications for the work permits module.
    """

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
    """Формує короткі рядки стану пошти та джерел НПА для Dashboard.
    Builds short mail and NPA source status lines for the Dashboard.
    """

    latest_mail = _find_latest_entry(audit_entries, "reports_mail")
    latest_news = _find_latest_entry(audit_entries, "news_npa")
    return (
        _format_service_line("Пошта", latest_mail),
        _format_service_line("Джерела НПА", latest_news),
    )


# ###### ОСТАННЯ ПОДІЯ МОДУЛЯ / LATEST MODULE EVENT ######
def _find_latest_entry(audit_entries: tuple[AuditLogEntry, ...], module_name: str) -> AuditLogEntry | None:
    """Повертає останню audit-подію потрібного зовнішнього модуля.
    Returns the latest audit event for the requested external module.
    """

    for audit_entry in audit_entries:
        if audit_entry.module_name == module_name:
            return audit_entry
    return None


# ###### ФОРМАТ СЛУЖБОВОГО РЯДКА / SERVICE LINE FORMAT ######
def _format_service_line(title: str, audit_entry: AuditLogEntry | None) -> str:
    """Перетворює audit-подію на зрозумілий службовий статус.
    Converts an audit event into a readable service status.
    """

    if audit_entry is None:
        return f"{title}: подій ще немає"
    return f"{title}: {audit_entry.result_status} | {audit_entry.event_type} | {audit_entry.created_at_text}"
