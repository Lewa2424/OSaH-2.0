from datetime import date, timedelta


# ###### ПОСТРОЕНИЕ ДЕМО-ЗАПИСЕЙ ИНСТРУКТАЖЕЙ / BUILD DEMO TRAINING ROWS ######
def build_demo_training_rows(
    employee_rows: list[tuple[str, str, str, str, str]],
) -> list[tuple[str, str, str, str, str, str, str, int, str, str, str, str, str, str, str]]:
    """Возвращает демонстрационные записи инструктажей с новыми нормативными полями.
    Returns demo training records with the new normative fields populated.
    """

    today = date.today()
    rows: list[tuple[str, str, str, str, str, str, str, int, str, str, str, str, str, str, str]] = []
    active_employees = [row for row in employee_rows if row[4] == "active"]

    for index, employee_row in enumerate(active_employees):
        personnel_number = employee_row[0]
        if index % 9 == 0:
            continue

        event_date = today - timedelta(days=320 - (index % 25))
        next_control_date = today + timedelta(days=45 - (index % 80))
        training_type = "repeated"
        if index % 7 == 0:
            training_type = "primary"
        elif index % 5 == 0:
            training_type = "targeted"

        knowledge_check_result = "satisfactory"
        work_admission_status = "allowed"
        knowledge_check_note = "Проверка знаний проведена ответственным лицом."
        if training_type == "targeted" and index % 10 == 0:
            knowledge_check_result = "unsatisfactory"
            work_admission_status = "not_allowed"
            knowledge_check_note = "Целевой инструктаж завершен неудовлетворительным результатом."

        rows.append(
            (
                personnel_number,
                training_type,
                event_date.isoformat(),
                next_control_date.isoformat(),
                "Коваль Олена Вікторівна",
                "Плановий контроль знань з охорони праці.",
                "own_employee",
                1,
                "regular",
                "manual",
                knowledge_check_result,
                work_admission_status,
                knowledge_check_note,
                "Журнал інструктажів підприємства",
                "",
            )
        )

        if index % 6 == 0:
            extra_event_date = today - timedelta(days=35 + index)
            rows.append(
                (
                    personnel_number,
                    "unscheduled",
                    extra_event_date.isoformat(),
                    (extra_event_date + timedelta(days=180)).isoformat(),
                    "Іваненко Сергій Петрович",
                    "Позаплановий інструктаж після зміни технології робіт.",
                    "own_employee",
                    1,
                    "regular",
                    "manual",
                    "satisfactory",
                    "allowed",
                    "Внеплановый контроль знаний подтвержден.",
                    "Наказ про зміну технології робіт",
                    "",
                )
            )

    return rows
