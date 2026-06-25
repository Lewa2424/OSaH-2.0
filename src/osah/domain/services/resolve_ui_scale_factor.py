from osah.domain.entities.ui_scale_preset import UiScalePreset

_UI_SCALE_FACTORS: dict[UiScalePreset, float] = {
    UiScalePreset.COMPACT: 1.0,
    UiScalePreset.NORMAL: 1.15,
    UiScalePreset.LARGE: 1.25,
    UiScalePreset.XLARGE: 1.35,
}


# ###### КОЕФІЦІЄНТ МАСШТАБУ ІНТЕРФЕЙСУ / RESOLVE UI SCALE FACTOR ######
def resolve_ui_scale_factor(preset: UiScalePreset) -> float:
    """Повертає числовий коефіцієнт для обраного пресету масштабу.
    Returns the numeric factor for the selected UI scale preset.
    """

    return _UI_SCALE_FACTORS[preset]
