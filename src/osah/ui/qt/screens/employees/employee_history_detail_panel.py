from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QTextEdit, QVBoxLayout

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.domain.services.format_employee_audit_description_text import format_employee_audit_description_text
from osah.domain.services.format_employee_audit_event_label import format_employee_audit_event_label
from osah.domain.services.format_employee_audit_module_label import format_employee_audit_module_label
from osah.ui.qt.components.scrollable_horizontal_frame import ScrollableHorizontalFrame
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class EmployeeHistoryDetailPanel(QFrame):
    """Detail panel for the selected employee history entry. / Панель деталей вибраного запису історії працівника."""

    _DETAIL_MAX_HEIGHT = 260

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("employeeHistoryDetailPanel")
        self.setStyleSheet(
            f"""
            QFrame#employeeHistoryDetailPanel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F5F8FC);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xl']}px;
            }}
            QLabel#detailTitle {{
                color: {COLOR['text_primary']};
                font-size: 18px;
                font-weight: 900;
            }}
            QLabel#detailHint {{
                color: {COLOR['text_muted']};
                font-size: 14px;
                font-weight: 600;
            }}
            QFrame#detailMeta {{
                background: #F6F9FC;
                border: 1px solid #E1E8EF;
                border-radius: {RADIUS['lg']}px;
            }}
            QLabel#detailMetaText {{
                color: {COLOR['text_secondary']};
                font-size: 13px;
                font-weight: 700;
                line-height: 1.5;
            }}
            QTextEdit {{
                background: transparent;
                color: {COLOR['text_primary']};
                font-size: 14px;
                border: none;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Деталі запису")
        title.setObjectName("detailTitle")
        layout.addWidget(title)

        self._hint_label = QLabel("Оберіть запис в історії вище, щоб побачити подію, модуль і розгорнутий опис.")
        self._hint_label.setObjectName("detailHint")
        self._hint_label.setWordWrap(True)
        layout.addWidget(self._hint_label)

        self._meta_frame = QFrame()
        self._meta_frame.setObjectName("detailMeta")
        meta_layout = QVBoxLayout(self._meta_frame)
        meta_layout.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["sm"])
        meta_layout.setSpacing(0)

        self._meta_label = QLabel("")
        self._meta_label.setObjectName("detailMetaText")
        self._meta_label.setWordWrap(True)
        self._meta_label.setTextFormat(Qt.TextFormat.PlainText)
        meta_layout.addWidget(self._meta_label)
        layout.addWidget(self._meta_frame)

        self._description_scroll = QScrollArea()
        self._description_scroll.setWidgetResizable(True)
        self._description_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._description_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._description_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._description_scroll.setMaximumHeight(self._DETAIL_MAX_HEIGHT)
        self._description_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._description_text = QTextEdit()
        self._description_text.setReadOnly(True)
        self._description_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self._description_text.setFrameShape(QFrame.Shape.NoFrame)
        self._description_scroll.setWidget(self._description_text)

        self._description_frame = ScrollableHorizontalFrame(self._description_scroll)
        self._description_frame.hide()
        layout.addWidget(self._description_frame)

        self.show_placeholder()

    def set_entry(self, audit_entry: AuditLogEntry) -> None:
        """Shows the selected audit entry in a user-readable format. / Показує вибраний audit-запис."""

        self._hint_label.hide()
        self._meta_frame.show()
        self._description_frame.show()
        self._meta_label.setText(
            "\n".join(
                (
                    f"Модуль: {format_employee_audit_module_label(audit_entry.module_name)}",
                    f"Подія: {format_employee_audit_event_label(audit_entry.event_type)}",
                    f"Результат: {_build_result_label(audit_entry.result_status)}",
                    f"Час: {audit_entry.created_at_text}",
                )
            )
        )
        self._description_text.setPlainText(format_employee_audit_description_text(audit_entry.description_text))

    def show_placeholder(self) -> None:
        """Shows a neutral state before selecting a history entry. / Показує нейтральний стан до вибору запису."""

        self._hint_label.show()
        self._meta_frame.hide()
        self._description_frame.hide()
        self._meta_label.clear()
        self._description_text.clear()


def _build_result_label(result_status: str) -> str:
    normalized_status = result_status.strip().lower()
    if normalized_status == "success":
        return "успішно"
    if normalized_status == "failed":
        return "помилка"
    return result_status or "невідомо"
