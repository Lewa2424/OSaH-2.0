from datetime import date, timedelta


# ###### ПОБУДОВА ДЕМО-ЗАПИСІВ ІНСТРУКТАЖІВ / ПОСТРОЕНИЕ ДЕМО-ЗАПИСЕЙ ИНСТРУКТАЖЕЙ ######
def build_demo_training_rows(employee_rows: list[tuple[str, str, str, str, str]]) -> list[tuple[str, str, str, str, str, str]]:
    """Повертає демонстраційні записи інструктажів з різними статусними сценаріями.
    Возвращает демонстрационные записи инструктажей с разными статусными сценариями.
    """

    today = date.today()
    rows: list[tuple[str, str, str, str, str, str]] = []
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
        rows.append(
            (
                personnel_number,
                training_type,
                event_date.isoformat(),
                next_control_date.isoformat(),
                "Коваль Олена Вікторівна",
                "Плановий контроль знань з охорони праці.",
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
                )
            )

    return rows
