import secrets


# ###### ГЕНЕРАЦІЯ RECOVERY-КОДУ / ГЕНЕРАЦИЯ RECOVERY-КОДА ######
def generate_recovery_code() -> str:
    """Генерує код аварійного відновлення для локальної установки.
    Генерирует код аварийного восстановления для локальной установки.
    """

    raw_code = secrets.token_hex(6).upper()
    return f"{raw_code[:4]}-{raw_code[4:8]}-{raw_code[8:12]}"
