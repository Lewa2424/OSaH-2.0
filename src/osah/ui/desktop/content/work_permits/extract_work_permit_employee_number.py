from tkinter import StringVar


# ###### ВИДІЛЕННЯ ТАБЕЛЬНОГО НОМЕРА ДЛЯ НАРЯДУ / ВЫДЕЛЕНИЕ ТАБЕЛЬНОГО НОМЕРА ДЛЯ НАРЯДА ######
def extract_work_permit_employee_number(selected_employee_var: StringVar) -> str:
    """Повертає табельний номер з підпису обраного учасника наряду-допуску.
    Возвращает табельный номер из подписи выбранного участника наряда-допуска.
    """

    selected_option = selected_employee_var.get().strip()
    if " | " not in selected_option:
        return ""
    return selected_option.split(" | ", maxsplit=1)[0].strip()
