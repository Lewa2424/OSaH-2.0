from dataclasses import dataclass

from osah.domain.entities.ui_scale_preset import UiScalePreset


@dataclass(frozen=True, slots=True)
class UiScalePresetPresentation:
    """Підписи пресету масштабу для UI.
    UI labels for a UI scale preset.
    """

    title: str
    hint: str


_UI_SCALE_PRESENTATIONS: dict[UiScalePreset, UiScalePresetPresentation] = {
    UiScalePreset.COMPACT: UiScalePresetPresentation("Компактний", ""),
    UiScalePreset.NORMAL: UiScalePresetPresentation("Звичайний", "для ноутбука"),
    UiScalePreset.LARGE: UiScalePresetPresentation("Збільшений", ""),
    UiScalePreset.XLARGE: UiScalePresetPresentation("Великий", "максимум"),
}


# ###### ПІДПИС ПРЕСЕТУ МАСШТАБУ / FORMAT UI SCALE PRESET LABEL ######
def format_ui_scale_preset_presentation(preset: UiScalePreset) -> UiScalePresetPresentation:
    """Повертає заголовок і підказку для плитки пресету масштабу.
    Returns the title and hint for a UI scale preset tile.
    """

    return _UI_SCALE_PRESENTATIONS[preset]
