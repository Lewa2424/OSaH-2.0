from PySide6.QtGui import QFont

from osah.domain.entities.ui_scale_preset import UiScalePreset
from osah.domain.services.resolve_ui_scale_factor import resolve_ui_scale_factor

_UI_SCALE_FACTOR = 1.0


# ###### ІНІЦІАЛІЗАЦІЯ МАСШТАБУ ІНТЕРФЕЙСУ / INIT UI SCALE ######
def init_ui_scale(preset: UiScalePreset) -> float:
    """Встановлює глобальний коефіцієнт масштабу для Qt UI.
    Sets the global scale factor for the Qt UI layer.
    """

    global _UI_SCALE_FACTOR
    _UI_SCALE_FACTOR = resolve_ui_scale_factor(preset)
    return _UI_SCALE_FACTOR


# ###### ПОТОЧНИЙ КОЕФІЦІЄНТ МАСШТАБУ / GET UI SCALE FACTOR ######
def get_ui_scale_factor() -> float:
    """Повертає активний коефіцієнт масштабу інтерфейсу.
    Returns the active UI scale factor.
    """

    return _UI_SCALE_FACTOR


# ###### МАСШТАБОВАНЕ ЗНАЧЕННЯ В PX / SCALED PX ######
def scaled_px(value: int | float) -> int:
    """Масштабує піксельне значення згідно з активним пресетом.
    Scales a pixel value according to the active preset.
    """

    return max(1, round(float(value) * _UI_SCALE_FACTOR))


# ###### БАЗОВИЙ ШРИФТ ЗАСТОСУНКУ / BUILD APPLICATION FONT ######
def build_application_font() -> QFont:
    """Повертає базовий шрифт застосунку з урахуванням масштабу.
    Returns the application base font with the active scale applied.
    """

    font = QFont("Segoe UI", scaled_px(11))
    return font
