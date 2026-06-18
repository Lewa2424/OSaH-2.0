import html
import re

_BULLET_LINE_PATTERN = re.compile(r"^[\u2022•\-–]\s+")


def format_ai_chat_message_html(author: str, text: str) -> str:
    """Форматує текст повідомлення AI-чату в HTML зі списками та переносами.
    Formats AI chat message text as HTML with lists and line breaks.
    """

    lines = text.splitlines()
    body_parts: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        if not list_items:
            return
        body_parts.append("<ul style='margin:6px 0 6px 18px;padding:0;'>")
        for item in list_items:
            body_parts.append(f"<li style='margin:2px 0;'>{item}</li>")
        body_parts.append("</ul>")
        list_items.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_list()
            continue
        if _BULLET_LINE_PATTERN.match(stripped):
            list_items.append(html.escape(_BULLET_LINE_PATTERN.sub("", stripped, count=1)))
            continue
        flush_list()
        body_parts.append(f"{html.escape(stripped)}<br>")

    flush_list()
    body_html = "".join(body_parts).rstrip("<br>")
    return f"<b>{html.escape(author)}</b><br>{body_html}"
