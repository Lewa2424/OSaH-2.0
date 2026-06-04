from osah.domain.services.security.validate_single_program_access_password import (
    validate_single_program_access_password,
)


# ###### ПЕРЕВІРКА ПАРОЛІВ ДОСТУПУ / ПРОВЕРКА ПАРОЛЕЙ ДОСТУПА ######
def validate_program_access_passwords(inspector_password: str, manager_password: str) -> None:
    """Перевіряє базові вимоги до паролів інспектора і керівника.
    Проверяет базовые требования к паролям инспектора и руководителя.
    """

    normalized_inspector_password = validate_single_program_access_password(
        inspector_password,
        "інспектора",
    )
    normalized_manager_password = validate_single_program_access_password(
        manager_password,
        "керівника",
    )
    if normalized_inspector_password == normalized_manager_password:
        raise ValueError("Паролі інспектора і керівника повинні відрізнятися.")
