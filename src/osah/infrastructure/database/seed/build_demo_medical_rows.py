from datetime import date, timedelta


# ###### ПОБУДОВА ДЕМО-ЗАПИСІВ МЕДИЦИНИ / ПОСТРОЕНИЕ ДЕМО-ЗАПИСЕЙ МЕДИЦИНЫ ######
def build_demo_medical_rows(employee_rows: list[tuple[str, str, str, str, str]]) -> list[tuple[str, str, str, str, str]]:
    """Повертає демонстраційні записи меддопусків з нормою, обмеженнями та простроченням.
    Возвращает демонстрационные записи меддопусков с нормой, ограничениями и просрочкой.
    """

    today = date.today()
    rows: list[tuple[str, str, str, str, str]] = []

    for index, employee_row in enumerate(row for row in employee_rows if row[4] == "active"):
        personnel_number = employee_row[0]
        valid_from = today - timedelta(days=280 - (index % 30))
        valid_until = today + timedelta(days=40 - (index % 95))
        if index % 11 == 0:
            medical_decision = "not_fit"
            restriction_note = "Тимчасово відсторонений до повторного медогляду."
        elif index % 6 == 0:
            medical_decision = "restricted"
            restriction_note = "Без робіт на висоті та без нічних змін."
        else:
            medical_decision = "fit"
            restriction_note = ""
        rows.append(
            (
                personnel_number,
                valid_from.isoformat(),
                valid_until.isoformat(),
                medical_decision,
                restriction_note,
            )
        )

    return rows
