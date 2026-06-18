import re

_EXAMPLE_HINTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(?:покаж|список|кого|хто|кто|працівник|сотрудник|подраздел|підрозділ)", re.IGNORECASE),
        "«Покажи стропальщиков», «Кто работает в подразделении Лаборатория?»",
    ),
    (
        re.compile(r"(?:каск|зіз|сиз|ppe|перчат|рукавиц|спецодяг)", re.IGNORECASE),
        "«Кому не видали каску?», «Видай каски всім стропальникам»",
    ),
    (
        re.compile(r"(?:інструктаж|инструктаж|train)", re.IGNORECASE),
        "«Покажи просроченные инструктажи», «Занеси инструктаж Иванову»",
    ),
    (
        re.compile(r"(?:наряд|допуск|permit)", re.IGNORECASE),
        "«Покажи наряды на сегодня», «Додай Петренка до наряду №5»",
    ),
    (
        re.compile(r"(?:мед|медогляд|медосмотр)", re.IGNORECASE),
        "«Покажи медогляди», «Продли медогляд Иванову»",
    ),
    (
        re.compile(r"(?:port[\s-]?r|порт[\s-]?р|ризик)", re.IGNORECASE),
        "«Покажи пробелы PORT-R», «Что такое оценка рисков?»",
    ),
)


def build_unknown_intent_clarification_message(raw_command: str) -> str:
    """Формує підказку з прикладами, якщо намір команди не розпізнано.
    Builds example hints when the command intent is not recognized.
    """

    command = raw_command.strip()
    examples: list[str] = []
    for pattern, hint in _EXAMPLE_HINTS:
        if pattern.search(command):
            examples.append(hint)
        if len(examples) >= 2:
            break

    if not examples:
        examples = [
            "«Покажи просроченные инструктажи»",
            "«Видай каски всім стропальникам дільниці N2»",
        ]

    joined = "; ".join(examples[:2])
    return f"Намір команди не розпізнано. Спробуйте, наприклад: {joined}."
