# ###### ІНТЕРПОЛЯЦІЯ HEX-КОЛЬОРІВ / HEX COLOR INTERPOLATION ######
def interpolate_hex_colors(color_a: str, color_b: str, ratio: float) -> str:
    """Повертає проміжний колір між двома hex-значеннями.
    Returns an intermediate color between two hex values.
    """

    clamped_ratio = max(0.0, min(1.0, ratio))
    red_a, green_a, blue_a = _parse_hex_color(color_a)
    red_b, green_b, blue_b = _parse_hex_color(color_b)
    red = int(red_a + (red_b - red_a) * clamped_ratio)
    green = int(green_a + (green_b - green_a) * clamped_ratio)
    blue = int(blue_a + (blue_b - blue_a) * clamped_ratio)
    return f"#{red:02x}{green:02x}{blue:02x}"


# ###### РОЗБІР HEX-КОЛЬОРУ / PARSE HEX COLOR ######
def _parse_hex_color(color: str) -> tuple[int, int, int]:
    """Перетворює #RRGGBB у RGB-кортеж.
    Converts #RRGGBB into an RGB tuple.
    """

    normalized = color.lstrip("#")
    if len(normalized) != 6:
        raise ValueError(f"Unsupported color format: {color}")
    return int(normalized[0:2], 16), int(normalized[2:4], 16), int(normalized[4:6], 16)
