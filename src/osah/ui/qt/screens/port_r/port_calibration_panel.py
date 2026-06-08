from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.port_compensating_barrier_item import PortCompensatingBarrierItem
from osah.domain.entities.port_macrovariable import MACROVARIABLE_ORDER, PortMacrovariable, format_macrovariable
from osah.domain.entities.port_macrovariable_threshold import PortMacrovariableThreshold
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING

_CALIB_FONT_BODY = 13
_CALIB_FONT_CAPTION = 12
_HEADER_RIGHT_AIR = 5
_ROW_CONTROL_HEIGHT = 40
_ROW_VERTICAL_GAP = SPACING["sm"]
_K_SPIN_WIDTH = 70
_K_COMP_SPIN_WIDTH = 82
_STOP_ROW_OBJECT_NAME = "portCalibrationStopRow"

_ICON_DIR = Path(__file__).resolve().parents[2] / "assets" / "icons"
_ARROW_UP_URL = (_ICON_DIR / "chevron_up_accent.svg").as_posix()
_ARROW_DOWN_URL = (_ICON_DIR / "chevron_down_accent.svg").as_posix()


@dataclass
class _ThresholdRow:
    trigger_input: QLineEdit
    k_spin: QDoubleSpinBox
    stop_check: QCheckBox
    del_btn: QPushButton
    row_widget: QWidget


@dataclass
class _BarrierRow:
    name_input: QLineEdit
    desc_input: QLineEdit
    k_comp_spin: QDoubleSpinBox
    del_btn: QPushButton
    row_widget: QWidget


def _line_edit_stylesheet(*, stop: bool = False) -> str:
    text_color = COLOR["status_critical"] if stop else COLOR["input_text"]
    weight = "bold" if stop else "normal"
    return (
        f"font-size: {_CALIB_FONT_BODY}px;"
        f" color: {text_color};"
        f" font-weight: {weight};"
        f" background: {COLOR['input_bg']};"
        f" border: 1px solid {COLOR['input_border']};"
        f" border-radius: {RADIUS['md']}px;"
        f" padding: 6px 10px;"
        f" min-height: 22px;"
    )


def _spin_box_stylesheet() -> str:
    radius = RADIUS["md"]
    return (
        f"QDoubleSpinBox {{"
        f" font-size: {_CALIB_FONT_BODY}px;"
        f" color: {COLOR['input_text']};"
        f" background: {COLOR['input_bg']};"
        f" border: 1px solid {COLOR['input_border']};"
        f" border-radius: {radius}px;"
        f" padding: 2px 22px 2px 8px;"
        f" min-height: 22px;"
        f"}}"
        f"QDoubleSpinBox:focus {{"
        f" border: 1px solid {COLOR['input_border_focus']};"
        f"}}"
        f"QDoubleSpinBox::up-button {{"
        f" subcontrol-origin: border;"
        f" subcontrol-position: top right;"
        f" width: 18px;"
        f" border-left: 1px solid {COLOR['border_soft']};"
        f" border-bottom: 1px solid {COLOR['border_soft']};"
        f" background: {COLOR['accent_soft']};"
        f" border-top-right-radius: {radius - 1}px;"
        f"}}"
        f"QDoubleSpinBox::down-button {{"
        f" subcontrol-origin: border;"
        f" subcontrol-position: bottom right;"
        f" width: 18px;"
        f" border-left: 1px solid {COLOR['border_soft']};"
        f" background: {COLOR['accent_soft']};"
        f" border-bottom-right-radius: {radius - 1}px;"
        f"}}"
        f"QDoubleSpinBox::up-button:hover,"
        f"QDoubleSpinBox::down-button:hover {{"
        f" background: {COLOR['nav_item_hover_bg']};"
        f"}}"
        f"QDoubleSpinBox::up-arrow {{"
        f" image: url({_ARROW_UP_URL});"
        f" width: 11px;"
        f" height: 11px;"
        f"}}"
        f"QDoubleSpinBox::down-arrow {{"
        f" image: url({_ARROW_DOWN_URL});"
        f" width: 11px;"
        f" height: 11px;"
        f"}}"
    )


def _delete_button_stylesheet() -> str:
    return (
        f"padding: 0px;"
        f" font-size: 15px;"
        f" color: {COLOR['text_primary']};"
        f" background: {COLOR['button_secondary_bg']};"
        f" border: 1px solid {COLOR['button_secondary_border']};"
        f" border-radius: {RADIUS['md']}px;"
    )


def _style_line_edit(line_edit: QLineEdit, *, stop: bool = False) -> None:
    line_edit.setFixedHeight(_ROW_CONTROL_HEIGHT)
    line_edit.setStyleSheet(_line_edit_stylesheet(stop=stop))


def _style_spin_box(spin: QDoubleSpinBox) -> None:
    spin.setFixedHeight(_ROW_CONTROL_HEIGHT)
    spin.setStyleSheet(_spin_box_stylesheet())


def _style_delete_button(button: QPushButton) -> None:
    button.setFixedSize(_ROW_CONTROL_HEIGHT, _ROW_CONTROL_HEIGHT)
    button.setProperty("variant", "secondary")
    button.setFont(QFont("Segoe UI Emoji", 13))
    button.setStyleSheet(_delete_button_stylesheet())


def _make_info_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    label.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["sm"])
    label.setStyleSheet(
        f"color: {COLOR['text_secondary']};"
        f" font-size: {_CALIB_FONT_BODY}px;"
        f" padding: {SPACING['sm']}px {SPACING['md']}px;"
        f" background: {COLOR['bg_workspace']};"
        f" border: 1px solid {COLOR['border_soft']};"
        f" border-radius: {RADIUS['md']}px;"
    )
    return label


def _make_caption_label(text: str, *, fixed_width: int | None = None, center: bool = False) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: {_CALIB_FONT_CAPTION}px;")
    if fixed_width is not None:
        label.setFixedWidth(fixed_width)
    if center:
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


def _make_add_button(title: str, example_a: str, example_b: str) -> QPushButton:
    button = QPushButton()
    button.setProperty("variant", "secondary")
    button.setMinimumHeight(36)
    button.setStyleSheet(f"padding: 6px 16px; font-size: {_CALIB_FONT_BODY}px; text-align: left;")

    layout = QHBoxLayout(button)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(SPACING["sm"])

    title_label = QLabel(title)
    title_label.setStyleSheet(
        f"font-size: {_CALIB_FONT_BODY}px; color: {COLOR['text_primary']}; background: transparent;"
    )
    title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    examples_label = QLabel(f"напр.: <i>{example_a}</i> або <i>{example_b}</i>")
    examples_label.setTextFormat(Qt.TextFormat.RichText)
    examples_label.setStyleSheet(
        f"font-size: {_CALIB_FONT_CAPTION}px; color: {COLOR['text_muted']}; background: transparent;"
    )
    examples_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    layout.addWidget(title_label)
    layout.addWidget(examples_label, stretch=1)
    return button


def _make_delete_button(*, tooltip: str = "Видалити рядок") -> QPushButton:
    button = QPushButton("🗑")
    button.setToolTip(tooltip)
    _style_delete_button(button)
    return button


def _apply_stop_row_highlight(row_widget: QWidget, is_stop: bool) -> None:
    row_widget.setObjectName(_STOP_ROW_OBJECT_NAME)
    background = COLOR["status_critical_bg"] if is_stop else "transparent"
    row_widget.setStyleSheet(
        f"QWidget#{_STOP_ROW_OBJECT_NAME} {{"
        f" background-color: {background};"
        f" border-radius: {RADIUS['md']}px;"
        f" padding: 2px;"
        f"}}"
    )


def _style_threshold_row(row: _ThresholdRow) -> None:
    is_stop = row.stop_check.isChecked()
    _apply_stop_row_highlight(row.row_widget, is_stop)
    _style_line_edit(row.trigger_input, stop=is_stop)
    _style_spin_box(row.k_spin)
    _style_delete_button(row.del_btn)
    row.stop_check.setStyleSheet(f"font-size: {_CALIB_FONT_BODY}px; background: transparent;")


def _style_barrier_row(row: _BarrierRow) -> None:
    _style_line_edit(row.name_input)
    _style_line_edit(row.desc_input)
    _style_spin_box(row.k_comp_spin)
    _style_delete_button(row.del_btn)


def _build_group_box(title: str) -> QGroupBox:
    group = QGroupBox(title)
    group.setStyleSheet(
        f"QGroupBox {{ font-size: {_CALIB_FONT_BODY}px; font-weight: bold; }}"
        f" QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; }}"
    )
    return group


_THRESHOLDS_INFO_TEXT = (
    "Калібрування динамічного контуру: для кожної макрозмінної (Т-П-С-В-Б) задайте умови "
    "відхилення від штатного режиму роботи на ділянці.\n\n"
    "K — множник деградації (1.0 = норма, до 2.0 = подвоєений ризик). У формулі "
    "R_dyn = R_base × K_т × K_п × K_с × K_в × K_б множаться лише спрацьовані тригери зміни.\n\n"
    "Позначка СТОП — критичне відхилення: зміна негайно переводиться в червону зону "
    "незалежно від числового R_dyn. Ці пороги використовуються майстром у чек-листі зміни."
)

_BARRIERS_INFO_TEXT = (
    "Компенсуючі бар'єри згруповані за макрозмінними (Т-П-С-В-Б): заходи, які знижують ризик "
    "у жовтій зоні (R_dyn від 1.41 до 1.80).\n\n"
    "K_comp — знижувальний множник (< 1.0). Чим менше значення, тим сильніший ефект бар'єра "
    "в розрахунку R_dyn.\n\n"
    "Якщо під час оцінки зміни R_dyn потрапляє в жовту зону, майстер обирає один бар'єр "
    "зі списку перед продовженням робіт."
)

_THRESHOLD_ADD_EXAMPLES: dict[PortMacrovariable, tuple[str, str]] = {
    PortMacrovariable.T: ("знос стропів", "несправність"),
    PortMacrovariable.P: ("нестача бригади", "втома зміни"),
    PortMacrovariable.S: ("туман", "сильний вітер"),
    PortMacrovariable.V: ("пошкоджена упаковка", "зміщення ЦТ"),
    PortMacrovariable.B: ("збій зв'язку", "немає огородження"),
}

_BARRIER_ADD_EXAMPLES: dict[PortMacrovariable, tuple[str, str]] = {
    PortMacrovariable.T: ("зменшення швидкості", "додатковий огляд ВЗП"),
    PortMacrovariable.P: ("додатковий сигнальник", "зменшення складу"),
    PortMacrovariable.S: ("освітлення зони", "перенесення робіт"),
    PortMacrovariable.V: ("додаткове кріплення", "зменшення партії"),
    PortMacrovariable.B: ("тимчасове огородження", "посилений зв'язок"),
}


class PortThresholdsPanel(QWidget):
    """Панель редагування порогів відхилення для макрозмінних Т-П-С-В-Б."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: dict[PortMacrovariable, list[_ThresholdRow]] = {mv: [] for mv in MACROVARIABLE_ORDER}
        self._section_layouts: dict[PortMacrovariable, QVBoxLayout] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(_HEADER_RIGHT_AIR, 0, _HEADER_RIGHT_AIR, 0)
        layout.setSpacing(SPACING["md"])
        layout.addWidget(_make_info_label(_THRESHOLDS_INFO_TEXT))

        for mv in MACROVARIABLE_ORDER:
            layout.addWidget(self._build_macrovariable_group(mv))
        layout.addStretch()

    def _build_macrovariable_group(self, mv: PortMacrovariable) -> QGroupBox:
        group = _build_group_box(format_macrovariable(mv))
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["md"])
        group_layout.setSpacing(SPACING["sm"])

        rows_container = QWidget()
        rows_layout = QVBoxLayout(rows_container)
        rows_layout.setContentsMargins(0, 0, _HEADER_RIGHT_AIR, 0)
        rows_layout.setSpacing(_ROW_VERTICAL_GAP)
        self._section_layouts[mv] = rows_layout

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING["sm"])
        header_layout.addWidget(_make_caption_label("Тригер відхилення"), stretch=1)
        header_layout.addWidget(_make_caption_label("K", fixed_width=_K_SPIN_WIDTH, center=True))
        header_layout.addWidget(_make_caption_label("СТОП", fixed_width=48, center=True))
        del_spacer = QLabel("")
        del_spacer.setFixedWidth(_ROW_CONTROL_HEIGHT)
        header_layout.addWidget(del_spacer)
        rows_layout.addWidget(header)

        group_layout.addWidget(rows_container)

        ex_a, ex_b = _THRESHOLD_ADD_EXAMPLES[mv]
        add_btn = _make_add_button("+ Додати тригер", ex_a, ex_b)
        add_btn.clicked.connect(lambda: self._add_threshold_row(mv))
        group_layout.addWidget(add_btn)
        return group

    def _add_threshold_row(
        self,
        mv: PortMacrovariable,
        trigger_text: str = "",
        k_value: float = 1.2,
        is_stop: bool = False,
    ) -> None:
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING["sm"])

        trigger_input = QLineEdit()
        trigger_input.setPlaceholderText("Опис умови відхилення")
        trigger_input.setText(trigger_text)

        k_spin = QDoubleSpinBox()
        k_spin.setRange(1.0, 2.0)
        k_spin.setSingleStep(0.1)
        k_spin.setDecimals(1)
        k_spin.setValue(k_value)
        k_spin.setFixedWidth(_K_SPIN_WIDTH)
        k_spin.setToolTip("Множник K (1.0 — 2.0)")

        stop_check = QCheckBox()
        stop_check.setChecked(is_stop)
        stop_check.setFixedWidth(48)
        stop_check.setToolTip("Критичний тригер — негайний СТОП")

        del_btn = _make_delete_button()

        row_layout.addWidget(trigger_input, stretch=1)
        row_layout.addWidget(k_spin)
        row_layout.addWidget(stop_check)
        row_layout.addWidget(del_btn)

        threshold_row = _ThresholdRow(
            trigger_input=trigger_input,
            k_spin=k_spin,
            stop_check=stop_check,
            del_btn=del_btn,
            row_widget=row_widget,
        )
        stop_check.toggled.connect(lambda _checked, row=threshold_row: _style_threshold_row(row))
        del_btn.clicked.connect(lambda: self._remove_threshold_row(mv, threshold_row))

        self._rows[mv].append(threshold_row)
        self._section_layouts[mv].addWidget(row_widget)
        _style_threshold_row(threshold_row)

    def _remove_threshold_row(self, mv: PortMacrovariable, row: _ThresholdRow) -> None:
        if row in self._rows[mv]:
            self._rows[mv].remove(row)
        row.row_widget.setParent(None)
        row.row_widget.deleteLater()

    def load_thresholds(self, thresholds: tuple[PortMacrovariableThreshold, ...]) -> None:
        for mv in MACROVARIABLE_ORDER:
            for row in list(self._rows[mv]):
                row.row_widget.setParent(None)
                row.row_widget.deleteLater()
            self._rows[mv].clear()

        for threshold in thresholds:
            self._add_threshold_row(
                threshold.macrovariable,
                trigger_text=threshold.trigger_text,
                k_value=threshold.k_value,
                is_stop=threshold.is_stop_trigger,
            )

    def collect_thresholds(self) -> list[tuple[PortMacrovariable, str, float, bool]]:
        result: list[tuple[PortMacrovariable, str, float, bool]] = []
        for mv in MACROVARIABLE_ORDER:
            for row in self._rows[mv]:
                text = row.trigger_input.text().strip()
                if text:
                    result.append((mv, text, row.k_spin.value(), row.stop_check.isChecked()))
        return result


class PortBarriersPanel(QWidget):
    """Панель редагування компенсуючих бар'єрів по макрозмінних Т-П-С-В-Б."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: dict[PortMacrovariable, list[_BarrierRow]] = {mv: [] for mv in MACROVARIABLE_ORDER}
        self._section_layouts: dict[PortMacrovariable, QVBoxLayout] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(_HEADER_RIGHT_AIR, 0, _HEADER_RIGHT_AIR, 0)
        outer.setSpacing(SPACING["md"])
        outer.addWidget(_make_info_label(_BARRIERS_INFO_TEXT))

        for mv in MACROVARIABLE_ORDER:
            outer.addWidget(self._build_macrovariable_group(mv))
        outer.addStretch()

    def _build_macrovariable_group(self, mv: PortMacrovariable) -> QGroupBox:
        group = _build_group_box(format_macrovariable(mv))
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["md"])
        group_layout.setSpacing(SPACING["sm"])

        rows_container = QWidget()
        rows_layout = QVBoxLayout(rows_container)
        rows_layout.setContentsMargins(0, 0, _HEADER_RIGHT_AIR, 0)
        rows_layout.setSpacing(_ROW_VERTICAL_GAP)
        self._section_layouts[mv] = rows_layout

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING["sm"])
        header_layout.addWidget(_make_caption_label("Назва бар'єра"), stretch=1)
        header_layout.addWidget(_make_caption_label("Опис / дія"), stretch=2)
        header_layout.addWidget(_make_caption_label("K_comp", fixed_width=_K_COMP_SPIN_WIDTH, center=True))
        del_spacer = QLabel("")
        del_spacer.setFixedWidth(_ROW_CONTROL_HEIGHT)
        header_layout.addWidget(del_spacer)
        rows_layout.addWidget(header)

        group_layout.addWidget(rows_container)

        ex_a, ex_b = _BARRIER_ADD_EXAMPLES[mv]
        add_btn = _make_add_button("+ Додати бар'єр", ex_a, ex_b)
        add_btn.clicked.connect(lambda: self._add_barrier_row(mv))
        group_layout.addWidget(add_btn)
        return group

    def _add_barrier_row(
        self,
        mv: PortMacrovariable,
        name: str = "",
        desc: str = "",
        k_comp: float = 0.9,
    ) -> None:
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING["sm"])

        name_input = QLineEdit()
        name_input.setPlaceholderText("Назва бар'єра")
        name_input.setText(name)

        desc_input = QLineEdit()
        desc_input.setPlaceholderText("Опис дії / умови застосування")
        desc_input.setText(desc)

        k_comp_spin = QDoubleSpinBox()
        k_comp_spin.setRange(0.50, 0.99)
        k_comp_spin.setSingleStep(0.05)
        k_comp_spin.setDecimals(2)
        k_comp_spin.setValue(k_comp)
        k_comp_spin.setFixedWidth(_K_COMP_SPIN_WIDTH)
        k_comp_spin.setToolTip("Знижувальний множник (< 1.0). Чим менший — тим сильніший ефект.")

        del_btn = _make_delete_button(tooltip="Видалити бар'єр")

        row_layout.addWidget(name_input, stretch=1)
        row_layout.addWidget(desc_input, stretch=2)
        row_layout.addWidget(k_comp_spin)
        row_layout.addWidget(del_btn)

        barrier_row = _BarrierRow(
            name_input=name_input,
            desc_input=desc_input,
            k_comp_spin=k_comp_spin,
            del_btn=del_btn,
            row_widget=row_widget,
        )
        del_btn.clicked.connect(lambda: self._remove_barrier_row(mv, barrier_row))

        self._rows[mv].append(barrier_row)
        self._section_layouts[mv].addWidget(row_widget)
        _style_barrier_row(barrier_row)

    def _remove_barrier_row(self, mv: PortMacrovariable, row: _BarrierRow) -> None:
        if row in self._rows[mv]:
            self._rows[mv].remove(row)
        row.row_widget.setParent(None)
        row.row_widget.deleteLater()

    def load_barriers(self, barriers: tuple[PortCompensatingBarrierItem, ...]) -> None:
        for mv in MACROVARIABLE_ORDER:
            for row in list(self._rows[mv]):
                row.row_widget.setParent(None)
                row.row_widget.deleteLater()
            self._rows[mv].clear()

        for barrier in barriers:
            self._add_barrier_row(
                barrier.macrovariable,
                name=barrier.barrier_name,
                desc=barrier.description,
                k_comp=barrier.k_comp,
            )

    def collect_barriers(self) -> list[tuple[PortMacrovariable, str, str, float]]:
        result: list[tuple[PortMacrovariable, str, str, float]] = []
        for mv in MACROVARIABLE_ORDER:
            for row in self._rows[mv]:
                name = row.name_input.text().strip()
                if name:
                    result.append((mv, name, row.desc_input.text().strip(), row.k_comp_spin.value()))
        return result
