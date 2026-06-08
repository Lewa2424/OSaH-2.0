from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NavFillPalette:
    """120 кольорів сегментів діаграми nav-кнопки.
    120 segment colors for a nav-button fill diagram.
    """

    colors: tuple[str, ...]
