# ###### ФОРМАТ ЗАЛИШКУ ЧАСУ DEMO / FORMAT DEMO REMAINING DURATION ######
def format_demo_remaining_duration(remaining_seconds: int) -> str:
    """Форматує залишок часу demo у зрозумілий для користувача рядок.
    Formats remaining demo time as a user-friendly string.
    """

    total_minutes = max(0, remaining_seconds // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours > 0:
        return f"{hours} год {minutes} хв"
    return f"{minutes} хв"
