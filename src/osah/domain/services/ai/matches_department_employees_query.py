from osah.domain.services.ai.extract_workplace_span import extract_workplace_span


def extract_department_employees_query(raw_command: str) -> str | None:
    """Витягує назву підрозділу з питання «хто працює в …».
    Extracts a department name from a who-works-in-department question.
    """

    return extract_workplace_span(raw_command)
