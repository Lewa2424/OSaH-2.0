from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QStackedLayout, QVBoxLayout, QWidget

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.services.build_news_source_display_name import build_news_source_display_name
from osah.ui.qt.components.alert_card import AlertCard
from osah.ui.qt.components.screen_states import EmptyStateWidget
from osah.ui.qt.design.tokens import COLOR, FONT, SPACING
from osah.ui.qt.screens.dashboard.dashboard_motion import AmbientDashboardWidget, DashboardGlassFrame, SlideRevealFrame
from osah.ui.qt.screens.dashboard.dashboard_widgets import DashboardFeedCard, DashboardModuleCard, DashboardStatCard


class DashboardScreen(QWidget):
    """Builds dashboard screen. / Создает экран дашборда."""

    employee_attention_requested = Signal(str, str)
    trainings_attention_requested = Signal(str)
    ppe_attention_requested = Signal(str)
    medical_attention_requested = Signal(str)
    work_permits_attention_requested = Signal(str)

    def __init__(self, snapshot: DashboardSnapshot, service_audit_entries: tuple[AuditLogEntry, ...] = ()) -> None:
        """Initializes dashboard layout. / Инициализирует компоновку дашборда."""
        super().__init__()
        root_layout = QStackedLayout(self)
        root_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        root_layout.setContentsMargins(0, 0, 0, 0)

        background = AmbientDashboardWidget()
        root_layout.addWidget(background)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
            "QScrollArea QWidget#dashboardCanvas { background: transparent; }"
        )
        root_layout.addWidget(scroll)
        root_layout.setCurrentWidget(scroll)

        canvas = QWidget()
        canvas.setObjectName("dashboardCanvas")
        scroll.setWidget(canvas)

        layout = QVBoxLayout(canvas)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["xl"])

        layout.addWidget(self._build_hero_panel(snapshot))
        layout.addWidget(self._build_metrics_row(snapshot))
        layout.addWidget(self._build_quick_contours_row(snapshot))

        sections_layout = QHBoxLayout()
        sections_layout.setSpacing(SPACING["xl"])
        sections_layout.addWidget(self._wrap_reveal(self._build_alerts_panel(snapshot), 250), stretch=7)

        right_column_reveal = SlideRevealFrame()
        right_column_reveal.set_reveal_delay(340)
        right_column_layout = right_column_reveal.content_layout()
        right_column_layout.setSpacing(SPACING["lg"])
        right_column_layout.addWidget(self._build_news_panel(snapshot))
        right_column_layout.addWidget(self._build_service_panel(service_audit_entries))
        right_column_layout.addStretch()
        sections_layout.addWidget(right_column_reveal, stretch=5)

        sections_host = QWidget()
        sections_host_layout = QHBoxLayout(sections_host)
        sections_host_layout.setContentsMargins(0, 0, 0, 0)
        sections_host_layout.addLayout(sections_layout)
        layout.addWidget(sections_host)
        layout.addStretch()

    def _build_hero_panel(self, snapshot: DashboardSnapshot) -> SlideRevealFrame:
        """Builds top hero block. / Создает верхний hero-блок."""
        reveal = SlideRevealFrame()
        focus_panel = DashboardGlassFrame(border_color=COLOR["news_accent"], fill_ratio=0.85)
        focus_layout = QVBoxLayout(focus_panel)
        focus_layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        focus_layout.setSpacing(4)

        focus_label = QLabel("Фокус дня")
        focus_label.setStyleSheet(
            f"color: {COLOR['news_accent']}; font-size: 14px; font-weight: 800; letter-spacing: 0.8px; background: transparent;"
        )
        focus_layout.addWidget(focus_label)

        focus_text = QLabel(snapshot.focus_of_the_day or "Сьогодні система не призначила окремий оперативний фокус.")
        focus_text.setWordWrap(True)
        focus_text.setStyleSheet(
            f"color: {COLOR['text_primary']}; font-size: 18px; font-weight: 700; background: transparent;"
        )
        focus_layout.addWidget(focus_text)

        reveal.content_layout().addWidget(focus_panel)
        return reveal

    def _build_metrics_row(self, snapshot: DashboardSnapshot) -> SlideRevealFrame:
        """Builds KPI row. / Создает ряд KPI-карточек."""
        reveal = SlideRevealFrame()
        reveal.set_reveal_delay(110)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(SPACING["lg"])
        reveal.content_layout().addLayout(metrics_layout)

        metrics_layout.addWidget(
            DashboardStatCard("Контур персоналу", snapshot.employee_total, "Працівники у локальній базі", COLOR["accent"])
        )
        metrics_layout.addWidget(
            DashboardStatCard("Критичний тиск", snapshot.critical_items, "Недопуски, прострочки, блокери", COLOR["critical"])
        )
        metrics_layout.addWidget(
            DashboardStatCard("Ризикова хвиля", snapshot.warning_items, "Порогові сигнали, що ростуть", COLOR["warning"])
        )
        metrics_layout.addWidget(
            DashboardStatCard("Нові матеріали", snapshot.unread_news_total, "НПА та новини без перегляду", COLOR["news_accent"])
        )
        return reveal

    def _build_quick_contours_row(self, snapshot: DashboardSnapshot) -> SlideRevealFrame:
        """Builds quick contours row. / Создает ряд быстрых контуров."""
        training_critical, training_warning = _count_training_notifications(snapshot)
        ppe_critical, ppe_warning = _count_ppe_notifications(snapshot)
        medical_critical, medical_warning = _count_medical_notifications(snapshot)
        permit_critical, permit_warning = _count_work_permit_notifications(snapshot)

        reveal = SlideRevealFrame()
        reveal.set_reveal_delay(180)
        shell = DashboardGlassFrame(border_color=COLOR["critical"], fill_ratio=0.92)
        reveal.content_layout().addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        shell_layout.setSpacing(SPACING["sm"])

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(SPACING["lg"])

        trainings_card = DashboardModuleCard(
            title="Інструктажі",
            caption="Прострочки, відсутні записи, плин ризику в навчанні.",
            critical_count=training_critical,
            warning_count=training_warning,
            accent_color=COLOR["critical"] if training_critical else COLOR["warning"],
            action_label="Відкрити контур інструктажів",
        )
        trainings_card.clicked.connect(
            lambda: self.trainings_attention_requested.emit("missing" if training_critical else "warning")
        )

        ppe_card = DashboardModuleCard(
            title="ЗІЗ",
            caption="Дефіцит видачі, ризик невідповідності, контроль забезпечення.",
            critical_count=ppe_critical,
            warning_count=ppe_warning,
            accent_color=COLOR["critical"] if ppe_critical else COLOR["warning"],
            action_label="Відкрити проблемні ЗІЗ",
        )
        ppe_card.clicked.connect(lambda: self.ppe_attention_requested.emit("not_issued" if ppe_critical else "warning"))

        medical_card = DashboardModuleCard(
            title="Медицина",
            caption="Меддопуск, обмеження, прострочки та критичні розриви.",
            critical_count=medical_critical,
            warning_count=medical_warning,
            accent_color=COLOR["critical"] if medical_critical else COLOR["warning"],
            action_label="Відкрити медичний контур",
        )
        medical_card.clicked.connect(
            lambda: self.medical_attention_requested.emit("expired" if medical_critical else "warning")
        )

        permits_card = DashboardModuleCard(
            title="Наряди-допуски",
            caption="Крайні строки, конфлікти складу та небезпечні активні роботи.",
            critical_count=permit_critical,
            warning_count=permit_warning,
            accent_color=COLOR["critical"] if permit_critical else COLOR["warning"],
            action_label="Відкрити контур нарядів",
        )
        permits_card.clicked.connect(
            lambda: self.work_permits_attention_requested.emit("expired" if permit_critical else "warning")
        )

        cards_layout.addWidget(trainings_card)
        cards_layout.addWidget(ppe_card)
        cards_layout.addWidget(medical_card)
        cards_layout.addWidget(permits_card)
        shell_layout.addLayout(cards_layout)
        return reveal

    def _build_alerts_panel(self, snapshot: DashboardSnapshot) -> QWidget:
        """Builds alerts panel. / Создает панель активных сигналов."""
        panel = DashboardGlassFrame(border_color=COLOR["critical"], fill_ratio=0.92)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Активні сповіщення")
        title.setStyleSheet(
            f"color: {COLOR['text_primary']}; font-size: 24px; font-weight: 900; background: transparent;"
        )
        layout.addWidget(title)

        subtitle = QLabel("Живий фронт проблемних сигналів з прямим переходом у контекст працівника.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color: {COLOR['text_secondary']}; font-size: 15px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(subtitle)

        if snapshot.active_notifications:
            alert_cards = []
            for notification in snapshot.active_notifications[:6]:
                card = AlertCard(notification)
                card.clicked.connect(lambda item=notification: self._emit_employee_attention(item))
                layout.addWidget(card)
                alert_cards.append(card)

            from osah.ui.qt.components.animations.stagger import apply_stagger

            apply_stagger(alert_cards, step_ms=120, duration=540)
        else:
            empty_state = EmptyStateWidget()
            empty_state.show_state(
                "Активних сповіщень немає.",
                "Система не бачить відкритих проблемних сигналів.",
            )
            layout.addWidget(empty_state)

        layout.addStretch()
        return panel

    def _build_news_panel(self, snapshot: DashboardSnapshot) -> QWidget:
        """Builds news panel. / Создает панель новостей и НПА."""
        panel = DashboardGlassFrame(border_color=COLOR["news_accent"], fill_ratio=0.92)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Новини та НПА")
        title.setStyleSheet(
            f"color: {COLOR['text_primary']}; font-size: 22px; font-weight: 900; background: transparent;"
        )
        layout.addWidget(title)

        subtitle = QLabel("Останні матеріали, що змінюють правовий або новинний контур безпеки.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color: {COLOR['text_secondary']}; font-size: 15px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(subtitle)

        if snapshot.latest_news_items:
            for news_item in snapshot.latest_news_items[:4]:
                kind_label = "НПА" if news_item.source_kind == NewsSourceKind.NPA else "Новина"
                source_label = build_news_source_display_name(news_item.source_name)
                layout.addWidget(
                    DashboardFeedCard(
                        title=news_item.title_text,
                        body=f"{kind_label} · {source_label}",
                        meta=news_item.published_at_text,
                        accent_color=COLOR["news_accent"],
                    )
                )
        else:
            empty_news = EmptyStateWidget()
            empty_news.show_state(
                "Нових матеріалів немає.",
                "Після перевірки джерел тут з'являться оновлення.",
            )
            layout.addWidget(empty_news)
        return panel

    def _build_service_panel(self, service_audit_entries: tuple[AuditLogEntry, ...]) -> QWidget:
        """Builds service panel. / Создает панель служебного контроля."""
        panel = DashboardGlassFrame(border_color=COLOR["accent"], fill_ratio=0.92)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Службовий контроль")
        title.setStyleSheet(
            f"color: {COLOR['text_primary']}; font-size: 22px; font-weight: 900; background: transparent;"
        )
        layout.addWidget(title)

        status_row = QHBoxLayout()
        status_row.setSpacing(SPACING["md"])
        live_chip = QLabel("SYSTEM LIVE")
        rgb = QColor(COLOR["success"])
        live_chip.setStyleSheet(
            f"background: rgba({rgb.red()}, {rgb.green()}, {rgb.blue()}, 28);"
            f"color: {COLOR['success']}; border: 1px solid {COLOR['success']}; border-radius: 12px; padding: 6px 12px; font-size: 11px; font-weight: 900;"
        )
        from osah.ui.qt.components.animations.pulse import apply_pulse

        apply_pulse(live_chip, min_opacity=0.5, beat_ms=780)
        status_row.addWidget(live_chip)
        status_row.addStretch()
        layout.addLayout(status_row)

        for service_status_text in _build_service_status_lines(service_audit_entries):
            service_title, _, service_body = service_status_text.partition(": ")
            layout.addWidget(
                DashboardFeedCard(
                    title=service_title,
                    body=service_body or service_status_text,
                    accent_color=COLOR["accent"],
                )
            )
        return panel

    def _wrap_reveal(self, widget: QWidget, delay_ms: int) -> SlideRevealFrame:
        """Wraps widget into reveal. / Оборачивает виджет в анимационный контейнер."""
        reveal = SlideRevealFrame()
        reveal.set_reveal_delay(delay_ms)
        reveal.content_layout().addWidget(widget)
        return reveal

    def _emit_employee_attention(self, notification: NotificationItem) -> None:
        """Emits employee attention request. / Отправляет запрос на открытие контекста сотрудника."""
        if notification.employee_personnel_number:
            self.employee_attention_requested.emit(
                notification.employee_personnel_number,
                notification.source_module,
            )


def _count_training_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Counts training signals. / Считает сигналы по инструктажам."""
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
    """Counts PPE signals. / Считает сигналы по ЗИЗ."""
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


def _count_medical_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Counts medical signals. / Считает сигналы по медицине."""
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


def _count_work_permit_notifications(snapshot: DashboardSnapshot) -> tuple[int, int]:
    """Counts work permit signals. / Считает сигналы по нарядам-допускам."""
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


def _build_service_status_lines(audit_entries: tuple[AuditLogEntry, ...]) -> tuple[str, ...]:
    """Builds service status lines. / Создает строки статусов сервисов."""
    latest_report = _find_latest_entry(audit_entries, "reports")
    latest_news = _find_latest_entry(audit_entries, "news_npa")
    return (
        _format_service_line("Щоденний звіт", latest_report),
        _format_service_line("Джерела новин і НПА", latest_news),
    )


def _find_latest_entry(audit_entries: tuple[AuditLogEntry, ...], module_name: str) -> AuditLogEntry | None:
    """Finds latest audit entry. / Находит последнее событие аудита."""
    for audit_entry in audit_entries:
        if audit_entry.module_name == module_name:
            return audit_entry
    return None


def _format_service_line(title: str, audit_entry: AuditLogEntry | None) -> str:
    """Formats service line. / Форматирует строку статуса сервиса."""
    if audit_entry is None:
        return f"{title}: подій ще не зафіксовано."
    if title == "Щоденний звіт":
        if audit_entry.event_type == "report.file_created":
            return f"{title}: файл сформовано {audit_entry.created_at_text}."
        if audit_entry.event_type == "report.settings_updated":
            return f"{title}: параметри нагадування оновлено {audit_entry.created_at_text}."
        return f"{title}: зафіксовано службову дію {audit_entry.created_at_text}."
    if audit_entry.event_type == "news.refresh_completed":
        return f"{title}: перевірку джерел завершено {audit_entry.created_at_text}."
    if audit_entry.event_type == "news.source_saved":
        return f"{title}: список джерел оновлено {audit_entry.created_at_text}."
    if audit_entry.event_type == "news.source_deleted":
        return f"{title}: джерело видалено {audit_entry.created_at_text}."
    if audit_entry.event_type == "news.source_activity_changed":
        return f"{title}: стан джерел змінено {audit_entry.created_at_text}."
    return f"{title}: зафіксовано службову дію {audit_entry.created_at_text}."
