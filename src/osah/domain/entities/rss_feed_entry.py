from dataclasses import dataclass


@dataclass(slots=True)
class RssFeedEntry:
    """Нормалізований запис зовнішнього RSS або Atom-каналу.
    Нормализованная запись внешнего RSS или Atom-канала.
    """

    title_text: str
    link_url: str
    published_at_text: str
