from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.create_port_shift_checklist import create_port_shift_checklist
from osah.application.services.load_port_calibration_for_passport import load_port_calibration_for_passport
from osah.domain.entities.port_compensating_barrier_item import PortCompensatingBarrierItem
from osah.domain.entities.port_macrovariable import MACROVARIABLE_ORDER, format_macrovariable
from osah.domain.entities.port_macrovariable_threshold import PortMacrovariableThreshold
from osah.domain.entities.port_passport_calibration import PortPassportCalibration
from osah.domain.entities.port_shift_decision import PortShiftDecision, format_port_shift_decision
from osah.domain.entities.port_shift_zone import (
    ZONE_GREEN_MAX,
    ZONE_YELLOW_MAX,
    PortShiftZone,
    format_port_shift_zone,
    zone_from_r_dyn,
)
from osah.domain.entities.port_site_passport_row import PortSitePassportRow
from osah.domain.services.calculate_dynamic_risk import calculate_dynamic_risk, combine_k_comp
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING

_ZONE_COLORS: dict[PortShiftZone, tuple[str, str]] = {
    PortShiftZone.GREEN: (COLOR["status_ok_bg"], COLOR["status_ok_text"]),
    PortShiftZone.YELLOW: (COLOR["status_warning_bg"], COLOR["status_warning_text"]),
    PortShiftZone.RED: (COLOR["status_critical_bg"], COLOR["status_critical_text"]),
}


class ShiftChecklistDialog(QDialog):
    """Діалог проведення оцінки зміни ПОРТ-Р: 5 блоків Т-П-С-В-Б, автозона, рішення.
    PORT-R shift assessment dialog: 5 T-P-S-V-B blocks, auto-zone, decision.
    """

    checklist_saved = Signal(int)

    def __init__(
        self,
        database_path: Path,
        passport_row: PortSitePassportRow,
        actor_name: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._database_path = database_path
        self._passport_row = passport_row
        self._actor_name = actor_name
        self._calibration: PortPassportCalibration | None = None
        self._trigger_checkboxes: dict[int, QCheckBox] = {}
        self._barrier_checkboxes: dict[int, QCheckBox] = {}

        self.setWindowTitle(f"Оцінка зміни — {passport_row.site_name}")
        self.setModal(True)
        self.resize(720, 760)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        root.setSpacing(SPACING["md"])

        root.addWidget(self._build_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(SPACING["md"])

        self._blocks_container = body_layout
        body_layout.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll, stretch=1)

        root.addWidget(self._build_rdyn_panel())
        root.addWidget(self._build_barrier_panel())
        root.addWidget(self._build_stop_panel())

        self._feedback = FormFeedbackLabel()
        root.addWidget(self._feedback)

        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        buttons.addStretch()
        self._save_btn = QPushButton("Зберегти оцінку")
        self._save_btn.setProperty("variant", "accent")
        self._save_btn.clicked.connect(self._save)
        buttons.addWidget(self._save_btn)
        root.addLayout(buttons)

        self._load_calibration()

    # ──────────────────────────────────────────────────────────────────────
    # Побудова UI / Build UI
    # ──────────────────────────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        widget = QWidget()
        outer = QVBoxLayout(widget)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(SPACING["xs"])

        subtitle = QLabel("Перенесення даних зі змінного листа майстра")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 12px;")
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        form_widget = QWidget()
        layout = QFormLayout(form_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])
        outer.addWidget(form_widget)

        import datetime
        today = datetime.date.today().isoformat()

        self._shift_date_input = QLineEdit(today)
        self._shift_date_input.setPlaceholderText("РРРР-ММ-ДД")
        layout.addRow("Дата зміни:", self._shift_date_input)

        self._shift_label_input = QLineEdit()
        self._shift_label_input.setPlaceholderText("Напр.: Зміна 1 / Ранкова / №3")
        layout.addRow("Позначення зміни:", self._shift_label_input)

        self._responsible_input = QLineEdit()
        self._responsible_input.setPlaceholderText("ПІБ відповідальної особи")
        layout.addRow("Відповідальний:", self._responsible_input)

        return widget

    def _build_rdyn_panel(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            f"QFrame {{ background: {COLOR['bg_workspace']}; border: 1px solid {COLOR['border_soft']}; border-radius: 6px; }}"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["sm"])
        layout.setSpacing(SPACING["md"])

        r_label = QLabel("R_dyn:")
        r_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(r_label)

        self._rdyn_value_label = QLabel("1.000")
        self._rdyn_value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self._rdyn_value_label)

        layout.addStretch()

        self._zone_badge = QLabel("Зона: —")
        self._zone_badge.setFixedHeight(28)
        self._zone_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zone_badge.setContentsMargins(SPACING["md"], 0, SPACING["md"], 0)
        self._zone_badge.setStyleSheet(
            f"background: {COLOR['bg_panel']}; border-radius: 4px; font-weight: bold; font-size: 12px;"
        )
        layout.addWidget(self._zone_badge)

        return frame

    def _build_barrier_panel(self) -> QWidget:
        self._barrier_widget = QWidget()
        layout = QVBoxLayout(self._barrier_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["xs"])

        barrier_label = QLabel(
            "Компенсуючі бар'єри (обов'язково в жовтій зоні; при 2+ тригерах — щонайменше 2):"
        )
        barrier_label.setWordWrap(True)
        barrier_label.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 11px;")
        layout.addWidget(barrier_label)

        self._barrier_checks_layout = QVBoxLayout()
        self._barrier_checks_layout.setContentsMargins(0, 0, 0, 0)
        self._barrier_checks_layout.setSpacing(SPACING["xs"])
        layout.addLayout(self._barrier_checks_layout)

        self._barrier_widget.setVisible(False)
        return self._barrier_widget

    def _build_stop_panel(self) -> QWidget:
        self._stop_widget = QWidget()
        layout = QVBoxLayout(self._stop_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["xs"])

        stop_label = QLabel("Причина зупинки / обставини (обов'язково при СТОП):")
        stop_label.setStyleSheet(f"color: {COLOR['status_critical']}; font-size: 11px; font-weight: bold;")
        layout.addWidget(stop_label)

        self._stop_reason_input = QTextEdit()
        self._stop_reason_input.setPlaceholderText("Опишіть причину зупинки робіт")
        self._stop_reason_input.setMaximumHeight(64)
        layout.addWidget(self._stop_reason_input)

        self._stop_widget.setVisible(False)
        return self._stop_widget

    # ──────────────────────────────────────────────────────────────────────
    # Завантаження калібрування / Load calibration
    # ──────────────────────────────────────────────────────────────────────

    def _load_calibration(self) -> None:
        try:
            self._calibration = load_port_calibration_for_passport(
                self._database_path, self._passport_row.passport_id
            )
        except Exception:
            self._calibration = None

        self._build_macrovariable_blocks()
        self._populate_barrier_checkboxes()
        self._recalculate()

    def _build_macrovariable_blocks(self) -> None:
        self._trigger_checkboxes.clear()

        stretch_item = self._blocks_container.takeAt(self._blocks_container.count() - 1)

        if self._calibration is None or not self._calibration.thresholds:
            empty_label = QLabel(
                "У паспорті ще не задано жодного тригера відхилення.\n"
                "Перейдіть до редагування паспорта і заповніть вкладку «Пороги Т-П-С-В-Б»."
            )
            empty_label.setWordWrap(True)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet(f"color: {COLOR['text_muted']}; padding: {SPACING['xl']}px;")
            self._blocks_container.addWidget(empty_label)
            self._blocks_container.addStretch()
            return

        thresholds_by_mv: dict = {mv: [] for mv in MACROVARIABLE_ORDER}
        for t in self._calibration.thresholds:
            thresholds_by_mv[t.macrovariable].append(t)

        for mv in MACROVARIABLE_ORDER:
            triggers = thresholds_by_mv[mv]
            if not triggers:
                continue
            group = QGroupBox(format_macrovariable(mv))
            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["sm"])
            group_layout.setSpacing(SPACING["xs"])

            for threshold in triggers:
                row = QWidget()
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(SPACING["sm"])

                cb = QCheckBox(threshold.trigger_text)
                cb.setChecked(False)
                cb.toggled.connect(self._recalculate)

                k_badge = QLabel(f"K={threshold.k_value:.1f}")
                k_badge.setFixedWidth(48)
                k_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                k_badge.setStyleSheet(
                    f"background: {COLOR['accent_soft']}; border-radius: 3px; font-size: 10px;"
                )

                if threshold.is_stop_trigger:
                    stop_badge = QLabel("СТОП")
                    stop_badge.setFixedWidth(40)
                    stop_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    stop_badge.setStyleSheet(
                        f"background: {COLOR['status_critical_bg']}; color: {COLOR['status_critical']};"
                        f" border-radius: 3px; font-size: 10px; font-weight: bold;"
                    )
                    cb.setStyleSheet(f"color: {COLOR['status_critical']};")
                    row_layout.addWidget(cb, stretch=1)
                    row_layout.addWidget(k_badge)
                    row_layout.addWidget(stop_badge)
                else:
                    row_layout.addWidget(cb, stretch=1)
                    row_layout.addWidget(k_badge)

                group_layout.addWidget(row)
                self._trigger_checkboxes[threshold.threshold_id] = cb

            self._blocks_container.addWidget(group)

        self._blocks_container.addStretch()

    def _populate_barrier_checkboxes(self) -> None:
        self._barrier_checkboxes.clear()
        while self._barrier_checks_layout.count():
            item = self._barrier_checks_layout.takeAt(0)
            child_layout = item.layout()
            if child_layout is not None:
                while child_layout.count():
                    nested = child_layout.takeAt(0)
                    nested_widget = nested.widget()
                    if nested_widget is not None:
                        nested_widget.deleteLater()
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if self._calibration is None or not self._calibration.compensating_barriers:
            empty = QLabel("У паспорті не задано компенсуючих бар'єрів.")
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 11px;")
            self._barrier_checks_layout.addWidget(empty)
            return

        for barrier in self._calibration.compensating_barriers:
            checkbox = QCheckBox(f"{barrier.barrier_name} (K_comp={barrier.k_comp:.2f})")
            checkbox.toggled.connect(self._recalculate)
            self._barrier_checkboxes[barrier.barrier_id] = checkbox
            self._barrier_checks_layout.addWidget(checkbox)

    # ──────────────────────────────────────────────────────────────────────
    # Розрахунок / Calculation
    # ──────────────────────────────────────────────────────────────────────

    def _recalculate(self) -> None:
        if self._calibration is None:
            return

        triggered_ids = self._get_triggered_ids()
        has_stop = self._has_stop_trigger(triggered_ids)

        k_values: list[float] = []
        for threshold in self._calibration.thresholds:
            if threshold.threshold_id in triggered_ids:
                k_values.append(threshold.k_value)

        k_comp = self._get_k_comp()

        if has_stop:
            zone = PortShiftZone.RED
            r_dyn = max(ZONE_YELLOW_MAX + 0.1, calculate_dynamic_risk(self._calibration.r_base, k_values, k_comp)[0])
        else:
            r_dyn, zone = calculate_dynamic_risk(self._calibration.r_base, k_values, k_comp)

        self._rdyn_value_label.setText(f"{r_dyn:.3f}")
        self._update_zone_badge(zone)
        self._update_panels(zone, has_stop)

    def _get_triggered_ids(self) -> list[int]:
        return [tid for tid, cb in self._trigger_checkboxes.items() if cb.isChecked()]

    def _has_stop_trigger(self, triggered_ids: list[int]) -> bool:
        if self._calibration is None:
            return False
        return any(t.is_stop_trigger and t.threshold_id in triggered_ids for t in self._calibration.thresholds)

    def _get_k_comp(self) -> float:
        if self._calibration is None:
            return 1.0
        k_values: list[float] = []
        for barrier_id, checkbox in self._barrier_checkboxes.items():
            if not checkbox.isChecked():
                continue
            for barrier in self._calibration.compensating_barriers:
                if barrier.barrier_id == barrier_id:
                    k_values.append(barrier.k_comp)
                    break
        return combine_k_comp(k_values)

    def _get_selected_barrier_ids(self) -> list[int]:
        return [barrier_id for barrier_id, checkbox in self._barrier_checkboxes.items() if checkbox.isChecked()]

    def _update_zone_badge(self, zone: PortShiftZone) -> None:
        bg, text_color = _ZONE_COLORS[zone]
        self._zone_badge.setText(format_port_shift_zone(zone))
        self._zone_badge.setStyleSheet(
            f"background: {bg}; color: {text_color}; border-radius: 4px;"
            f" font-weight: bold; font-size: 12px; padding: 0 {SPACING['md']}px;"
        )

    def _update_panels(self, zone: PortShiftZone, has_stop: bool) -> None:
        show_barrier = zone == PortShiftZone.YELLOW and not has_stop
        show_stop = zone == PortShiftZone.RED or has_stop
        self._barrier_widget.setVisible(show_barrier)
        self._stop_widget.setVisible(show_stop)

    # ──────────────────────────────────────────────────────────────────────
    # Збереження / Save
    # ──────────────────────────────────────────────────────────────────────

    def _save(self) -> None:
        shift_date = self._shift_date_input.text().strip()
        shift_label = self._shift_label_input.text().strip()
        responsible = self._responsible_input.text().strip()

        if not shift_date:
            self._feedback.show_error("Вкажіть дату зміни.")
            return
        if not responsible:
            self._feedback.show_error("Вкажіть відповідальну особу.")
            return

        triggered_ids = self._get_triggered_ids()
        has_stop = self._has_stop_trigger(triggered_ids)
        stop_reason = self._stop_reason_input.toPlainText().strip() if self._stop_widget.isVisible() else ""

        zone_raw = self._compute_current_zone(triggered_ids, has_stop)

        if zone_raw == PortShiftZone.YELLOW:
            barrier_ids = self._get_selected_barrier_ids()
            if not barrier_ids:
                self._feedback.show_error("У жовтій зоні оберіть хоча б один компенсуючий бар'єр.")
                return
            if len(triggered_ids) > 1 and len(barrier_ids) < 2:
                self._feedback.show_error(
                    "При двох і більше спрацьованих тригерах оберіть щонайменше два компенсуючі бар'єри."
                )
                return
        else:
            barrier_ids = []

        if zone_raw == PortShiftZone.RED and not stop_reason and has_stop:
            self._feedback.show_error("Вкажіть причину зупинки робіт.")
            return

        try:
            _, _, _, checklist_id = create_port_shift_checklist(
                self._database_path,
                passport_id=self._passport_row.passport_id,
                shift_date=shift_date,
                shift_label=shift_label,
                responsible_person=responsible,
                triggered_threshold_ids=triggered_ids,
                active_barrier_ids=barrier_ids,
                stop_reason=stop_reason,
                actor_name=self._actor_name,
            )
            self.checklist_saved.emit(checklist_id)
            self.accept()
        except Exception as error:
            self._feedback.show_error(str(error))

    def _compute_current_zone(self, triggered_ids: list[int], has_stop: bool) -> PortShiftZone:
        if has_stop:
            return PortShiftZone.RED
        if self._calibration is None:
            return PortShiftZone.GREEN
        k_values = [t.k_value for t in self._calibration.thresholds if t.threshold_id in triggered_ids]
        k_comp = self._get_k_comp()
        _, zone = calculate_dynamic_risk(self._calibration.r_base, k_values, k_comp)
        return zone
