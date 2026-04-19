from tkinter import StringVar


# ###### ВИДІЛЕННЯ ID ЗАПИСУ ІНСТРУКТАЖУ / ВЫДЕЛЕНИЕ ID ЗАПИСИ ИНСТРУКТАЖА ######
def extract_training_record_id(selected_record_var: StringVar) -> int | None:
    """Повертає ідентифікатор запису інструктажу з вибраного підпису.
    Возвращает идентификатор записи инструктажа из выбранной подписи.
    """

    selected_option = selected_record_var.get().strip()
    if " | " not in selected_option:
        return None
    record_id_text = selected_option.split(" | ", maxsplit=1)[0].strip()
    try:
        return int(record_id_text)
    except ValueError:
        return None
