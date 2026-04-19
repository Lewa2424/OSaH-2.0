# ###### ПОБУДОВА МАПИ ЗАГОЛОВКІВ ІМПОРТУ ПРАЦІВНИКІВ / ПОСТРОЕНИЕ КАРТЫ ЗАГОЛОВКОВ ИМПОРТА СОТРУДНИКОВ ######
def build_employee_import_header_map() -> dict[str, str]:
    """Повертає відповідність між підтриманими заголовками джерела та полями працівника.
    Возвращает соответствие между поддерживаемыми заголовками источника и полями сотрудника.
    """

    return {
        "personnel_number": "personnel_number",
        "табельний номер": "personnel_number",
        "табельный номер": "personnel_number",
        "full_name": "full_name",
        "піб": "full_name",
        "фио": "full_name",
        "position_name": "position_name",
        "посада": "position_name",
        "должность": "position_name",
        "department_name": "department_name",
        "підрозділ": "department_name",
        "подразделение": "department_name",
        "employment_status": "employment_status",
        "статус зайнятості": "employment_status",
        "статус занятости": "employment_status",
    }
