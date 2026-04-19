"""
DashboardScreen — заглушка головного екрана нового UI.
Використовує MetricCard, InfoPanel та AlertCard для відображення даних з DashboardSnapshot.
DashboardScreen — dashboard stub using new UI components for DashboardSnapshot.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.ui.qt.components.alert_card import AlertCard
from osah.ui.qt.components.metric_card import MetricCard
from osah.ui.qt.design.tokens import COLOR, SIZE, SPACING


class DashboardScreen(QWidget):
    """Екран Dashboard у новій Qt архітектурі.
    Dashboard screen assembled with new architecture components.
    """

    def __init__(self, snapshot: DashboardSnapshot) -> None:
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
                left_col.addWidget(AlertCard(n))
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
        
        btn1 = QPushButton("📝 Оформити наряд-допуск")
        btn1.setProperty("variant", "secondary")
        ib_layout.addWidget(btn1)
        
        btn2 = QPushButton("🛡️ Реєстрація інструктажу")
        btn2.setProperty("variant", "secondary")
        ib_layout.addWidget(btn2)
        
        ib_layout.addSpacing(SPACING["lg"])

        ib_msg = QLabel("Зведення виконання плану...")
        ib_msg.setProperty("role", "status_muted")
        ib_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ib_layout.addWidget(ib_msg)

        right_col.addWidget(info_box)
        right_col.addStretch()

        right_wrap = QWidget()
        right_wrap.setLayout(right_col)
        cols_layout.addWidget(right_wrap, stretch=4)

        layout.addLayout(cols_layout)
