from tkinter import StringVar


# ###### ВИДІЛЕННЯ ІДЕНТИФІКАТОРА НАРЯДУ / ВЫДЕЛЕНИЕ ИДЕНТИФИКАТОРА НАРЯДА ######
def extract_work_permit_record_id(selected_record_var: StringVar) -> int | None:
    """Повертає ідентифікатор наряду-допуску з підпису обраного запису.
    Возвращает идентификатор наряда-допуска из подписи выбранной записи.
    """

    selected_option = selected_record_var.get().strip()
    if " | " not in selected_option:
        return None
    record_id_text = selected_option.split(" | ", maxsplit=1)[0].strip()
    if not record_id_text.isdigit():
        return None
    return int(record_id_text)
