# ###### МАПІНГ СПОВІЩЕННЯ В ПРОБЛЕМУ / MAP NOTIFICATION TO PROBLEM ######
def map_notification_source_to_problem_key(source_module: str) -> str | None:
    """Повертає ключ проблемного контексту працівника за джерелом сповіщення.
    Returns an employee problem context key from a notification source.
    """

    source = source_module.lower()
    if "training" in source or "інструк" in source:
        return "trainings"
    if "ppe" in source or "зіз" in source or "сиз" in source:
        return "ppe"
    if "medical" in source or "мед" in source:
        return "medical"
    if "permit" in source or "наряд" in source:
        return "work_permits"
    return None
