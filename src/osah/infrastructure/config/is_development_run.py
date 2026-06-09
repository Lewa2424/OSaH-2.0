import sys


# ###### ЗАПУСК З ВИХІДНОГО КОДУ / DEVELOPMENT RUN DETECTION ######
def is_development_run() -> bool:
    """Повертає True для запуску з IDE або терміналу (не зібраний exe).
    Returns True when the app runs from source rather than a frozen build.
    """

    return not getattr(sys, "frozen", False)
