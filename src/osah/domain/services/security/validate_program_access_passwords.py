# ###### ПЕРЕВІРКА ПАРОЛІВ ДОСТУПУ / ПРОВЕРКА ПАРОЛЕЙ ДОСТУПА ######
def validate_program_access_passwords(inspector_password: str, manager_password: str) -> None:
    """Перевіряє базові вимоги до паролів інспектора і керівника.
    Проверяет базовые требования к паролям инспектора и руководителя.
    """

    normalized_inspector_password = inspector_password.strip()
    normalized_manager_password = manager_password.strip()

    if len(normalized_inspector_password) < 6:
        raise ValueError("Пароль інспектора має містити щонайменше 6 символів.")
    if len(normalized_manager_password) < 6:
        raise ValueError("Пароль керівника має містити щонайменше 6 символів.")
    if normalized_inspector_password == normalized_manager_password:
        raise ValueError("Паролі інспектора і керівника повинні відрізнятися.")
