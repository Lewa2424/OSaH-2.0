_KNOWN_MODULE_KEYS = frozenset(
    {
        "all",
        "ppe",
        "зіз",
        "сиз",
        "trainings",
        "інструктаж",
        "инструктаж",
        "medical",
        "мед",
        "work_permits",
        "наряд",
        "наряди",
        "employees",
        "працівник",
        "сотрудник",
        "port_r",
        "port-r",
    }
)


def normalize_ai_module_key(module_key: str | None) -> str:
    """Нормалізує module_key; невідомі значення зводить до all.
    Normalizes module_key; unknown values fall back to all.
    """

    normalized = (module_key or "all").strip().lower()
    if normalized in _KNOWN_MODULE_KEYS:
        return normalized
    return "all"
