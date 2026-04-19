from dataclasses import dataclass

from osah.domain.entities.news_item_read_state import NewsItemReadState
from osah.domain.entities.news_source_kind import NewsSourceKind


@dataclass(slots=True)
class NewsItem:
    """Кешований матеріал новинного або правового джерела.
    Кэшированный материал новостного или правового источника.
    """

    item_id: int
    source_id: int
    source_name: str
    source_kind: NewsSourceKind
    title_text: str
    link_url: str
    published_at_text: str
    read_state: NewsItemReadState
