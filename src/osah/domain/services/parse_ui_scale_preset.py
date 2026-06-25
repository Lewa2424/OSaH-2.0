from osah.domain.entities.ui_scale_preset import UiScalePreset


# ###### РОЗБІР ПРЕСЕТУ МАСШТАБУ / PARSE UI SCALE PRESET ######
def parse_ui_scale_preset(raw_value: str | None) -> UiScalePreset:
    """Повертає пресет масштабу з рядка налаштування або compact за замовчуванням.
    Returns a UI scale preset from a settings string or compact by default.
    """

    normalized_value = (raw_value or "").strip().casefold()
    for preset in UiScalePreset:
        if preset.value == normalized_value:
            return preset
    return UiScalePreset.COMPACT
