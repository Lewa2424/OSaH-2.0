from tkinter import StringVar


# ###### ВИТЯГ ІДЕНТИФІКАТОРА НОВИНИ З ВИБОРУ / ИЗВЛЕЧЕНИЕ ИДЕНТИФИКАТОРА НОВОСТИ ИЗ ВЫБОРА ######
def extract_news_item_id(selected_news_item_var: StringVar) -> int:
    """Повертає ідентифікатор новини з комбінованого рядка вибору.
    Возвращает идентификатор новости из комбинированной строки выбора.
    """

    selected_value = selected_news_item_var.get().strip()
    if not selected_value:
        raise ValueError("Потрібно вибрати матеріал.")
    return int(selected_value.split("|", maxsplit=1)[0].strip())
