from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from osah.domain.entities.access_role import AccessRole


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ЕКРАНА НОВИН / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ЭКРАНА НОВОСТЕЙ ######
def build_news_screen_refresh_handler(
    parent: ttk.Frame,
    database_path: Path,
    access_role: AccessRole,
) -> Callable[[], None]:
    """Повертає обробник перемальовування екрана новин і НПА.
    Возвращает обработчик перерисовки экрана новостей и НПА.
    """

    # ###### ОНОВЛЕННЯ ЕКРАНА НОВИН / ОБНОВЛЕНИЕ ЭКРАНА НОВОСТЕЙ ######
    def refresh_news_screen() -> None:
        """Перемальовує екран новин зі збереженням ролі доступу.
        Перерисовывает экран новостей с сохранением роли доступа.
        """

        from osah.ui.desktop.content.news.render_news_content import render_news_content

        for child in parent.winfo_children():
            child.destroy()
        render_news_content(parent, database_path, refresh_news_screen, access_role)

    return refresh_news_screen
