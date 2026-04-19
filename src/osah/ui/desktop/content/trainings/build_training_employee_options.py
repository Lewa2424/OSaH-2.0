from osah.domain.entities.employee import Employee


# ###### ПОБУДОВА ОПЦІЙ ПРАЦІВНИКІВ ДЛЯ ФОРМИ / ПОСТРОЕНИЕ ОПЦИЙ СОТРУДНИКОВ ДЛЯ ФОРМЫ ######
def build_training_employee_options(employees: tuple[Employee, ...]) -> tuple[str, ...]:
    """Повертає підписи працівників для вибору у формі інструктажу.
    Возвращает подписи сотрудников для выбора в форме инструктажа.
    """

    return tuple(f"{employee.personnel_number} | {employee.full_name}" for employee in employees)
