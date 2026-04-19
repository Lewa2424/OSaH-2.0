from dataclasses import dataclass

from osah.domain.entities.news_source_kind import NewsSourceKind


@dataclass(slots=True)
class NewsSource:
    """Довірене зовнішнє джерело новин або НПА.
    Доверенный внешний источник новостей или НПА.
    """

    source_id: int
    source_name: str
    source_url: str
    source_kind: NewsSourceKind
    is_active: bool
    is_trusted: bool
    last_checked_at_text: str
