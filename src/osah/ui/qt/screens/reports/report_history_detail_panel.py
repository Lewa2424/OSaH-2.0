from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ReportHistoryDetailPanel(QFrame):
    """Панель деталізації вибраної події доставки або формування звіту.
    Detail panel for the selected delivery or report generation event.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setProperty("card", "true")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["sm"])

        title = QLabel("Деталі події")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        self._hint_label = QLabel("Оберіть запис в історії вгорі, щоб побачити подробиці.")
        self._hint_label.setWordWrap(True)
        self._hint_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(self._hint_label)

        self._meta_label = QLabel("")
        self._meta_label.setWordWrap(True)
        self._meta_label.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(self._meta_label)

        self._description_label = QLabel("")
        self._description_label.setWordWrap(True)
        self._description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._description_label)

        self.show_placeholder()

    def set_entry(self, audit_entry: AuditLogEntry) -> None:
        """Показує поля вибраного audit-запису у зрозумілому для користувача вигляді.
        Shows selected audit entry fields in a user-readable way.
        """

        self._hint_label.hide()
        self._meta_label.setText(
            f"Подія: {audit_entry.event_type} • Результат: {audit_entry.result_status} • "
            f"Рівень: {audit_entry.event_level} • Час: {audit_entry.created_at_text}"
        )
        self._description_label.setText(audit_entry.description_text or "Опис події відсутній.")

    def show_placeholder(self) -> None:
        """Показує нейтральний стан до вибору запису історії.
        Shows a neutral state before selecting a history entry.
        """

        self._hint_label.show()
        self._meta_label.clear()
        self._description_label.clear()
