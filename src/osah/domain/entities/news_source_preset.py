from dataclasses import dataclass

from osah.domain.entities.news_source_kind import NewsSourceKind


@dataclass(slots=True, frozen=True)
class NewsSourcePreset:
    """Попередньо перевірене trusted-джерело з готовим RSS/Atom URL.
    Предварительно проверенный trusted-источник с готовым RSS/Atom URL.
    """

    source_name: str
    site_url: str
    source_url: str
    source_kind: NewsSourceKind
