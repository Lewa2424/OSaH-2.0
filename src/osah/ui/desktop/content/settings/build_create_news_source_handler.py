from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, messagebox

from osah.application.services.create_news_source import create_news_source
from osah.domain.entities.news_source_kind import NewsSourceKind


# ###### ПОБУДОВА ОБРОБНИКА ЗБЕРЕЖЕННЯ ДЖЕРЕЛА НОВИН / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОХРАНЕНИЯ ИСТОЧНИКА НОВОСТЕЙ ######
def build_create_news_source_handler(
    database_path: Path,
    source_name_var: StringVar,
    source_url_var: StringVar,
    source_kind_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник створення або оновлення довіреного джерела.
    Возвращает обработчик создания или обновления доверенного источника.
    """

    # ###### ЗБЕРЕЖЕННЯ ДЖЕРЕЛА НОВИН / СОХРАНЕНИЕ ИСТОЧНИКА НОВОСТЕЙ ######
    def save_news_source() -> None:
        """Зберігає джерело зовнішнього інформаційного контуру.
        Сохраняет источник внешнего информационного контура.
        """

        try:
            create_news_source(
                database_path=database_path,
                source_name=source_name_var.get(),
                source_url=source_url_var.get(),
                source_kind=NewsSourceKind(source_kind_var.get()),
            )
        except ValueError as error:
            messagebox.showerror("Помилка джерела", str(error))
            return

        messagebox.showinfo("Джерело збережено", "Довірене джерело новин або НПА оновлено у локальному контурі.")
        on_success()

    return save_news_source
