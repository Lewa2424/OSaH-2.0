from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.ui.qt.design.tokens import COLOR, SPACING


class ReportHistoryDetailPanel(QFrame):
    """Панель деталей вибраного запису історії звітів.
    Detail panel for the selected report history entry.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setProperty("card", "true")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["sm"])

        title = QLabel("Деталі запису")
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
        """Показує вибраний запис історії у зрозумілому вигляді.
        Shows the selected history entry in a user-readable format.
        """

        self._hint_label.hide()
        self._meta_label.setText(
            f"Подія: {_build_event_label(audit_entry.event_type)} • "
            f"Результат: {_build_result_label(audit_entry.result_status)} • "
            f"Час: {audit_entry.created_at_text}"
        )
        self._description_label.setText(_build_description_text(audit_entry.description_text))

    def show_placeholder(self) -> None:
        """Показує нейтральний стан до вибору запису історії.
        Shows a neutral state before selecting a history entry.
        """

        self._hint_label.show()
        self._meta_label.clear()
        self._description_label.clear()


def _build_event_label(event_type: str) -> str:
    """Повертає локалізовану назву події історії звітів.
    Returns a localized label for the report history event.
    """

    if event_type == "report.file_created":
        return "звіт сформовано"
    return event_type or "подія"


def _build_result_label(result_status: str) -> str:
    """Повертає локалізований підпис результату події.
    Returns a localized label for the event result.
    """

    normalized_status = result_status.strip().lower()
    if normalized_status == "success":
        return "успішно"
    if normalized_status == "failed":
        return "помилка"
    return result_status or "невідомо"


def _build_description_text(description_text: str) -> str:
    """Перетворює технічний audit-рядок на зрозумілий опис.
    Converts a technical audit string into a readable description.
    """

    if not description_text.strip():
        return "Опис події відсутній."

    user_file_path = _extract_value(description_text, "saved_path")
    internal_copy_path = _extract_value(description_text, "internal_copy")
    if user_file_path or internal_copy_path:
        parts: list[str] = []
        if user_file_path:
            parts.append(f"Файл користувача: {user_file_path}")
        if internal_copy_path:
            parts.append(f"Внутрішня копія: {internal_copy_path}")
        return "\n".join(parts)
    return description_text


def _extract_value(description_text: str, key_name: str) -> str:
    """Витягує значення за ключем із технічного опису журналу.
    Extracts a keyed value from the technical audit description.
    """

    key_token = f"{key_name}="
    if key_token not in description_text:
        return ""
    return description_text.split(key_token, maxsplit=1)[1].split(";", maxsplit=1)[0].strip()
