from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.entities.news_source_preset import NewsSourcePreset


# ###### СПИСОК ВБУДОВАНИХ RSS-ДЖЕРЕЛ / СПИСОК ВСТРОЕННЫХ RSS-ИСТОЧНИКОВ ######
def list_default_news_source_presets() -> tuple[NewsSourcePreset, ...]:
    """Повертає вбудований список перевірених RSS/Atom-джерел для швидкого додавання.
    Возвращает встроенный список проверенных RSS/Atom-источников для быстрого добавления.
    """

    return (
        NewsSourcePreset(
            source_name="Законодавство України — нові надходження",
            site_url="https://zakon.rada.gov.ua/laws/main/index",
            source_url="https://zakon.rada.gov.ua/laws/main/xml",
            source_kind=NewsSourceKind.NPA,
        ),
        NewsSourcePreset(
            source_name="Законодавство України — прийняті документи",
            site_url="https://zakon.rada.gov.ua/laws/main/index",
            source_url="https://zakon.rada.gov.ua/laws/main/nnn.xml",
            source_kind=NewsSourceKind.NPA,
        ),
        NewsSourcePreset(
            source_name="Верховна Рада України — RSS новин",
            site_url="https://www.rada.gov.ua/news",
            source_url="https://www.rada.gov.ua/rss",
            source_kind=NewsSourceKind.NPA,
        ),
        NewsSourcePreset(
            source_name="Держпраці України — RSS новин",
            site_url="https://dsp.gov.ua/",
            source_url="https://dsp.gov.ua/feed/",
            source_kind=NewsSourceKind.NEWS,
        ),
    )
