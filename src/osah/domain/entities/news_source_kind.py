from enum import StrEnum


class NewsSourceKind(StrEnum):
    """Тип зовнішнього інформаційного джерела.
    Тип внешнего информационного источника.
    """

    NEWS = "news"
    NPA = "npa"
