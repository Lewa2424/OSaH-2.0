from tkinter import StringVar


# ###### ВИДІЛЕННЯ ТАБЕЛЬНОГО НОМЕРА ДЛЯ МЕДИЦИНИ / ВЫДЕЛЕНИЕ ТАБЕЛЬНОГО НОМЕРА ДЛЯ МЕДИЦИНЫ ######
def extract_medical_employee_number(selected_employee_var: StringVar) -> str:
    """Повертає табельний номер з підпису обраного працівника.
    Возвращает табельный номер из подписи выбранного сотрудника.
    """

    selected_option = selected_employee_var.get().strip()
    if " | " not in selected_option:
        return ""
    return selected_option.split(" | ", maxsplit=1)[0].strip()
