# ###### ПЕРЕВІРКА ОДНОГО ПАРОЛЯ ДОСТУПУ / SINGLE ACCESS PASSWORD VALIDATION ######
def validate_single_program_access_password(password_text: str, role_label: str) -> str:
    """Повертає нормалізований пароль або піднімає ValueError.
    Returns normalized password or raises ValueError.
    """

    normalized_password = password_text.strip()
    if len(normalized_password) < 8:
        raise ValueError(f"Пароль {role_label} має містити щонайменше 8 символів.")
    return normalized_password
