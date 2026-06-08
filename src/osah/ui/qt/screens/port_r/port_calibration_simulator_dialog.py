from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.load_port_calibration_for_passport import load_port_calibration_for_passport
from osah.domain.entities.port_macrovariable import MACROVARIABLE_ORDER, format_macrovariable
from osah.domain.entities.port_passport_calibration import PortPassportCalibration
from osah.domain.entities.port_shift_zone import (
    ZONE_YELLOW_MAX,
    PortShiftZone,
    format_port_shift_zone,
)
from osah.domain.services.calculate_dynamic_risk import calculate_dynamic_risk, combine_k_comp
from osah.ui.qt.design.tokens import COLOR, SPACING

_ZONE_BADGE_STYLES: dict[PortShiftZone, str] = {
    PortShiftZone.GREEN: (
        f"background: {COLOR['status_ok_bg']}; color: {COLOR['status_ok_text']};"
        f" border-radius: 4px; padding: 4px 12px; font-weight: bold;"
    ),
    PortShiftZone.YELLOW: (
        f"background: {COLOR['status_warning_bg']}; color: {COLOR['status_warning_text']};"
        f" border-radius: 4px; padding: 4px 12px; font-weight: bold;"
    ),
    PortShiftZone.RED: (
        f"background: {COLOR['status_critical_bg']}; color: {COLOR['status_critical_text']};"
        f" border-radius: 4px; padding: 4px 12px; font-weight: bold;"
    ),
}


class PortCalibrationSimulatorDialog(QDialog):
    """Симулятор динамічного ризику ПОРТ-Р: «що буде з R_dyn / зоною», якщо спрацюють обрані тригери.
    PORT-R dynamic-risk simulator: "what happens to R_dyn / zone" if the selected triggers fire.
    """

    def __init__(
        self,
        database_path: Path,
        passport_id: int,
        passport_label: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._calibration: PortPassportCalibration | None = None
        self._trigger_checkboxes: dict[int, QCheckBox] = {}
        self._barrier_checkboxes: dict[int, QCheckBox] = {}

        title_suffix = f" — {passport_label}" if passport_label else ""
        self.setWindowTitle(f"Симулятор калібрування{title_suffix}")
        self.setModal(True)
        self.resize(620, 640)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        try:
            self._calibration = load_port_calibration_for_passport(database_path, passport_id)
        except Exception:  # noqa: BLE001
            self._calibration = None

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        root.setSpacing(SPACING["md"])

        subtitle = QLabel(
            "Оберіть гіпотетичні тригери та один або кілька бар'єрів, щоб побачити прогноз R_dyn і зони. Дані не зберігаються."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 12px;")
        root.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        self._blocks_container = QVBoxLayout(body)
        self._blocks_container.setContentsMargins(0, 0, 0, 0)
        self._blocks_container.setSpacing(SPACING["sm"])
        self._build_trigger_blocks()
        self._blocks_container.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll, stretch=1)

        barrier_title = QLabel("Компенсуючі бар'єри:")
        barrier_title.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 11px;")
        root.addWidget(barrier_title)

        self._barrier_checks_layout = QVBoxLayout()
        self._barrier_checks_layout.setContentsMargins(0, 0, 0, 0)
        self._barrier_checks_layout.setSpacing(SPACING["xs"])
        self._populate_barrier_checkboxes()
        root.addLayout(self._barrier_checks_layout)

        root.addWidget(self._build_result_panel())

        buttons = QHBoxLayout()
        buttons.addStretch()
        close_btn = QPushButton("Закрити")
        close_btn.setProperty("variant", "secondary")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)

        self._recalculate()

    # ──────────────────────────────────────────────────────────────────────
    # Побудова UI / UI builders
    # ──────────────────────────────────────────────────────────────────────

    def _build_trigger_blocks(self) -> None:
        if self._calibration is None or not self._calibration.thresholds:
            empty = QLabel("Для цього паспорта ще не задані пороги Т-П-С-В-Б.")
            empty.setStyleSheet(f"color: {COLOR['text_secondary']};")
            self._blocks_container.addWidget(empty)
            return

        thresholds_by_mv: dict = {mv: [] for mv in MACROVARIABLE_ORDER}
        for threshold in self._calibration.thresholds:
            thresholds_by_mv[threshold.macrovariable].append(threshold)

        for mv in MACROVARIABLE_ORDER:
            mv_triggers = thresholds_by_mv[mv]
            if not mv_triggers:
                continue
            title = QLabel(format_macrovariable(mv))
            title.setStyleSheet(f"color: {COLOR['text_primary']}; font-weight: bold;")
            self._blocks_container.addWidget(title)
            for threshold in mv_triggers:
                label = f"{threshold.trigger_text}  (K={threshold.k_value:.1f}"
                label += ", ⛔ СТОП)" if threshold.is_stop_trigger else ")"
                checkbox = QCheckBox(label)
                checkbox.toggled.connect(lambda *_: self._recalculate())
                self._trigger_checkboxes[threshold.threshold_id] = checkbox
                self._blocks_container.addWidget(checkbox)

    def _populate_barrier_checkboxes(self) -> None:
        self._barrier_checkboxes.clear()
        while self._barrier_checks_layout.count():
            item = self._barrier_checks_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if self._calibration is None or not self._calibration.compensating_barriers:
            empty = QLabel("Компенсуючі бар'єри не задані.")
            empty.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 11px;")
            self._barrier_checks_layout.addWidget(empty)
            return

        for barrier in self._calibration.compensating_barriers:
            checkbox = QCheckBox(f"{barrier.barrier_name} (K_comp={barrier.k_comp:.2f})")
            checkbox.toggled.connect(lambda *_: self._recalculate())
            self._barrier_checkboxes[barrier.barrier_id] = checkbox
            self._barrier_checks_layout.addWidget(checkbox)

    def _build_result_panel(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background: {COLOR['bg_workspace']}; border: 1px solid {COLOR['border_soft']};"
            f" border-radius: 6px; }}"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["sm"])
        layout.setSpacing(SPACING["md"])

        layout.addWidget(QLabel("Прогноз R_dyn:"))
        self._rdyn_value_label = QLabel("—")
        self._rdyn_value_label.setStyleSheet(
            f"color: {COLOR['text_primary']}; font-weight: bold; font-size: 16px;"
        )
        layout.addWidget(self._rdyn_value_label)
        layout.addStretch()

        self._zone_badge = QLabel("—")
        self._zone_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._zone_badge)
        return frame

    # ──────────────────────────────────────────────────────────────────────
    # Розрахунок / Calculation
    # ──────────────────────────────────────────────────────────────────────

    def _recalculate(self) -> None:
        if self._calibration is None:
            return

        triggered_ids = [tid for tid, cb in self._trigger_checkboxes.items() if cb.isChecked()]
        k_values = [
            threshold.k_value
            for threshold in self._calibration.thresholds
            if threshold.threshold_id in triggered_ids
        ]
        has_stop = any(
            threshold.is_stop_trigger and threshold.threshold_id in triggered_ids
            for threshold in self._calibration.thresholds
        )
        k_comp = self._selected_k_comp()

        if has_stop:
            zone = PortShiftZone.RED
            r_dyn = max(
                ZONE_YELLOW_MAX + 0.1,
                calculate_dynamic_risk(self._calibration.r_base, k_values, k_comp)[0],
            )
        else:
            r_dyn, zone = calculate_dynamic_risk(self._calibration.r_base, k_values, k_comp)

        self._rdyn_value_label.setText(f"{r_dyn:.3f}")
        self._zone_badge.setText(format_port_shift_zone(zone))
        self._zone_badge.setStyleSheet(_ZONE_BADGE_STYLES[zone])

    def _selected_k_comp(self) -> float:
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
