from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.port_macrovariable import format_macrovariable
from osah.domain.entities.port_shift_checklist_detail import PortShiftChecklistDetail
from osah.domain.entities.port_shift_decision import format_port_shift_decision
from osah.domain.entities.port_shift_zone import PortShiftZone, format_port_shift_zone
from osah.ui.qt.design.tokens import COLOR, SPACING

_ZONE_BADGE_STYLES: dict[PortShiftZone, str] = {
    PortShiftZone.GREEN: (
        f"background: {COLOR['status_ok_bg']}; color: {COLOR['status_ok_text']};"
        f" border-radius: 4px; padding: 3px 10px; font-weight: bold;"
    ),
    PortShiftZone.YELLOW: (
        f"background: {COLOR['status_warning_bg']}; color: {COLOR['status_warning_text']};"
        f" border-radius: 4px; padding: 3px 10px; font-weight: bold;"
    ),
    PortShiftZone.RED: (
        f"background: {COLOR['status_critical_bg']}; color: {COLOR['status_critical_text']};"
        f" border-radius: 4px; padding: 3px 10px; font-weight: bold;"
    ),
}


class PortShiftRecordDialog(QDialog):
    """Перегляд однієї оцінки зміни ПОРТ-Р (тільки читання) зі списком спрацьованих блоків.
    Read-only view of a single PORT-R shift assessment with the list of triggered blocks.
    """

    export_record_requested = Signal(int)

    def __init__(
        self,
        detail: PortShiftChecklistDetail,
        *,
        can_export: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._detail = detail
        row = detail.row

        self.setWindowTitle(f"Оцінка зміни — {row.shift_date} ({row.passport_code})")
        self.setModal(True)
        self.resize(620, 640)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        root.setSpacing(SPACING["md"])

        root.addWidget(self._build_header(row))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(SPACING["sm"])

        body_layout.addWidget(self._build_section_title("Спрацьовані блоки"))
        if detail.triggered_items:
            for item in detail.triggered_items:
                body_layout.addWidget(self._build_trigger_row(item))
        else:
            empty = QLabel("Жодного блоку не спрацювало — зміна в нормі.")
            empty.setStyleSheet(f"color: {COLOR['text_secondary']};")
            body_layout.addWidget(empty)

        if row.stop_reason:
            body_layout.addWidget(self._build_section_title("Причина зупинки / обставини"))
            stop_label = QLabel(row.stop_reason)
            stop_label.setWordWrap(True)
            stop_label.setStyleSheet(f"color: {COLOR['status_critical_text']};")
            body_layout.addWidget(stop_label)

        body_layout.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll, stretch=1)

        buttons = QHBoxLayout()
        if can_export:
            self._export_btn = QPushButton("Сформувати лист зі запису (.docx)")
            self._export_btn.setProperty("variant", "accent")
            self._export_btn.clicked.connect(self._on_export)
            buttons.addWidget(self._export_btn)
        buttons.addStretch()
        close_btn = QPushButton("Закрити")
        close_btn.setProperty("variant", "secondary")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

    # ──────────────────────────────────────────────────────────────────────
    # Побудова UI / UI builders
    # ──────────────────────────────────────────────────────────────────────

    def _build_header(self, row) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(SPACING["sm"])

        layout.addRow("Ділянка:", QLabel(f"{row.passport_code} / {row.site_name}"))
        layout.addRow("Дата зміни:", QLabel(row.shift_date or "—"))
        if row.shift_label:
            layout.addRow("Позначення зміни:", QLabel(row.shift_label))
        layout.addRow("Відповідальний:", QLabel(row.responsible_person or "—"))

        r_dyn_text = f"{row.r_dyn:.3f}" if row.r_dyn is not None else "—"
        layout.addRow("R_dyn:", QLabel(r_dyn_text))

        if row.zone is not None:
            zone_badge = QLabel(format_port_shift_zone(row.zone))
            zone_badge.setStyleSheet(_ZONE_BADGE_STYLES[row.zone])
            zone_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            zone_holder = QWidget()
            zone_holder_layout = QHBoxLayout(zone_holder)
            zone_holder_layout.setContentsMargins(0, 0, 0, 0)
            zone_holder_layout.addWidget(zone_badge)
            zone_holder_layout.addStretch()
            layout.addRow("Зона:", zone_holder)

        decision_text = format_port_shift_decision(row.decision) if row.decision else "—"
        layout.addRow("Рішення:", QLabel(decision_text))
        layout.addRow("Бар'єри:", QLabel(row.active_barrier_name or "—"))

        return widget

    def _build_section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {COLOR['text_primary']}; font-weight: bold; font-size: 13px;"
        )
        return label

    def _build_trigger_row(self, item) -> QFrame:
        frame = QFrame()
        border = COLOR["status_critical"] if item.is_stop_trigger else COLOR["border_soft"]
        frame.setStyleSheet(
            f"QFrame {{ background: {COLOR['bg_workspace']}; border: 1px solid {border};"
            f" border-radius: 6px; }}"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(SPACING["sm"], SPACING["xs"], SPACING["sm"], SPACING["xs"])
        layout.setSpacing(SPACING["sm"])

        block_label = QLabel(format_macrovariable(item.macrovariable))
        block_label.setStyleSheet(f"color: {COLOR['text_secondary']}; font-weight: bold;")
        block_label.setFixedWidth(120)
        layout.addWidget(block_label)

        trigger_label = QLabel(item.trigger_text or "—")
        trigger_label.setWordWrap(True)
        layout.addWidget(trigger_label, stretch=1)

        meta_text = f"K={item.k_used:.1f}"
        if item.is_stop_trigger:
            meta_text += "  ⛔ СТОП"
        meta_label = QLabel(meta_text)
        color = COLOR["status_critical_text"] if item.is_stop_trigger else COLOR["text_secondary"]
        meta_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(meta_label)

        return frame

    def _on_export(self) -> None:
        self.export_record_requested.emit(self._detail.row.checklist_id)
