from urllib.request import Request, urlopen


# ###### ЗАВАНТАЖЕННЯ WEB-ДОКУМЕНТА З URL / ЗАГРУЗКА WEB-ДОКУМЕНТА С URL ######
def read_web_document_from_url(source_url: str) -> tuple[str, str]:
    """Повертає content-type і текст документа, завантаженого з URL.
    Возвращает content-type и текст документа, загруженного с URL.
    """

    request = Request(
        source_url,
        headers={
            "User-Agent": "OSaH/2.0",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, text/html",
        },
    )
    with urlopen(request, timeout=20) as response:
        content_type = response.headers.get_content_type()
        document_text = response.read().decode("utf-8", errors="replace")
    return content_type, document_text
