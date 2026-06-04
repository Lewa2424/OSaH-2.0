from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox

from osah.application.services.refresh_news_sources import refresh_news_sources
from osah.domain.entities.access_role import AccessRole


# ###### ПОБУДОВА ОБРОБНИКА REFRESH ДЖЕРЕЛ НОВИН / ПОСТРОЕНИЕ ОБРАБОТЧИКА REFRESH ИСТОЧНИКОВ НОВОСТЕЙ ######
def build_refresh_news_sources_handler(
    database_path: Path,
    on_success: Callable[[], None],
    *,
    access_role: AccessRole,
) -> Callable[[], None]:
    """Повертає обробник ручного refresh зовнішніх джерел новин і НПА.
    Возвращает обработчик ручного refresh внешних источников новостей и НПА.
    """

    # ###### РУЧНИЙ REFRESH ДЖЕРЕЛ НОВИН / РУЧНОЙ REFRESH ИСТОЧНИКОВ НОВОСТЕЙ ######
    def refresh_news_sources_now() -> None:
        """Оновлює активні джерела і показує підсумок користувачу.
        Обновляет активные источники и показывает итог пользователю.
        """

        try:
            cached_item_total = refresh_news_sources(database_path, access_role=access_role)
        except Exception as error:
            messagebox.showerror("Помилка оновлення", str(error))
            return

        messagebox.showinfo("Оновлення завершено", f"У локальний кеш оброблено {cached_item_total} матеріалів.")
        on_success()

    return refresh_news_sources_now
