from collections.abc import Callable
from pathlib import Path
import customtkinter as ctk

from osah.application.services.load_news_items import load_news_items
from osah.application.services.load_news_sources import load_news_sources
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.is_access_role_read_only import is_access_role_read_only
from osah.ui.desktop.content.news.build_news_screen_refresh_handler import build_news_screen_refresh_handler
from osah.ui.desktop.content.news.render_news_actions import render_news_actions
from osah.ui.desktop.content.news.render_news_item_table import render_news_item_table
from osah.ui.desktop.content.news.render_news_source_table import render_news_source_table
from osah.ui.desktop.content.render_read_only_notice_card import render_read_only_notice_card
from osah.ui.desktop.content.render_screen_header import render_screen_header


# ###### ВІДОБРАЖЕННЯ ЕКРАНА НОВИН І НПА / ОТРИСОВКА ЭКРАНА НОВОСТЕЙ И НПА ######
def render_news_content(
    parent: ctk.CTkFrame,
    database_path: Path,
    on_refresh: Callable[[], None],
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> None:
    """Відображає зовнішній read-only контур новин і правових змін.
    Отрисовывает внешний read-only контур новостей и правовых изменений.
    """

    for child in parent.winfo_children():
        child.destroy()

    news_sources = load_news_sources(database_path)
    news_items = load_news_items(database_path)
    unread_news_items = load_news_items(database_path, unread_only=True)

    render_screen_header(
        parent,
        "Новини / НПА",
        "Зовнішній контур читає лише довірені джерела, кешує матеріали локально і не змінює внутрішні кадрові дані.",
    )

    if is_access_role_read_only(access_role):
        render_read_only_notice_card(
            parent,
            "Режим керівника",
            "Керівник переглядає локальний кеш новин і НПА без ручного refresh та без зміни статусів прочитання.",
        )
    else:
        refresh_handler = build_news_screen_refresh_handler(parent, database_path, access_role)
        render_news_actions(parent, database_path, unread_news_items, refresh_handler or on_refresh)

    render_news_source_table(parent, news_sources)
    render_news_item_table(parent, news_items)
