from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, messagebox

from osah.application.services.mark_news_item_as_read import mark_news_item_as_read
from osah.ui.desktop.content.news.extract_news_item_id import extract_news_item_id


# ###### ПОБУДОВА ОБРОБНИКА ПОЗНАЧЕННЯ НОВИНИ ЯК ПРОЧИТАНОЇ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ПОМЕТКИ НОВОСТИ КАК ПРОЧИТАННОЙ ######
def build_mark_news_item_as_read_handler(
    database_path: Path,
    selected_news_item_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник позначення вибраного матеріалу як прочитаного.
    Возвращает обработчик пометки выбранного материала как прочитанного.
    """

    # ###### ПОЗНАЧЕННЯ НОВИНИ ЯК ПРОЧИТАНОЇ / ПОМЕТКА НОВОСТИ КАК ПРОЧИТАННОЙ ######
    def mark_selected_news_item_as_read() -> None:
        """Оновлює read-state для вибраного матеріалу і перемальовує екран.
        Обновляет read-state для выбранного материала и перерисовывает экран.
        """

        try:
            item_id = extract_news_item_id(selected_news_item_var)
        except ValueError as error:
            messagebox.showerror("Помилка дії", str(error))
            return

        mark_news_item_as_read(database_path, item_id)
        messagebox.showinfo("Матеріал оновлено", "Новину або матеріал НПА позначено як прочитаний.")
        on_success()

    return mark_selected_news_item_as_read
