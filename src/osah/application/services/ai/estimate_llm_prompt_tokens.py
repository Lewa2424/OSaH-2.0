def estimate_llm_prompt_tokens(system_prompt: str, user_prompt: str) -> int:
    """Оцінює кількість токенів промпта (грубо: chars/3.5 для кирилиці).
    Estimates prompt token count (roughly chars/3.5 for Cyrillic-heavy text).
    """

    total_chars = len(system_prompt) + len(user_prompt)
    return max(1, int(total_chars / 3.5))


def is_llm_prompt_over_budget(
    system_prompt: str,
    user_prompt: str,
    *,
    max_tokens: int = 3200,
) -> bool:
    """Перевіряє, чи промпт перевищує практичний бюджет контексту.
    Checks whether the prompt exceeds the practical context budget.
    """

    return estimate_llm_prompt_tokens(system_prompt, user_prompt) > max_tokens
