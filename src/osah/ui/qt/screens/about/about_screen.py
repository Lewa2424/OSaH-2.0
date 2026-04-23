from osah.domain.entities.about_snapshot import AboutSnapshot
from osah.ui.qt.design.tokens import COLOR, SPACING
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AboutScreen(QWidget):
    """Informational About screen."""

    def __init__(self, snapshot: AboutSnapshot) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Про програму")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)

        subtitle = QLabel("Локальна система управління охороною праці для режиму 'встановив → налаштував → працюєш'.")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        info = QLabel(
            f"Продукт: {snapshot.product_name}\n"
            f"Версія: {snapshot.app_version}\n"
            f"Статус UI-контуру: {snapshot.ui_status}\n"
            f"Модель роботи: {snapshot.operation_model}\n"
            f"Поточна гілка: {snapshot.branch_name}\n\n"
            f"База даних: {snapshot.database_path}\n"
            f"Каталог даних: {snapshot.data_directory_path}\n"
            f"Лог-файл: {snapshot.log_path}\n\n"
            f"Кількість таблиць: {snapshot.table_count}\n"
            f"Кількість працівників: {snapshot.employee_count}\n"
            f"Непрочитані НПА/новини: {snapshot.unread_news_count}"
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()
