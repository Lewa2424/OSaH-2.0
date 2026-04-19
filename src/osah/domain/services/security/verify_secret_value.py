from hmac import compare_digest

from osah.domain.services.security.hash_secret_value import hash_secret_value


# ###### ПЕРЕВІРКА СЕКРЕТНОГО ЗНАЧЕННЯ / ПРОВЕРКА СЕКРЕТНОГО ЗНАЧЕНИЯ ######
def verify_secret_value(secret_value: str, salt_hex: str, expected_hash: str) -> bool:
    """Перевіряє пароль або код проти збереженого хешу.
    Проверяет пароль или код против сохранённого хеша.
    """

    return compare_digest(hash_secret_value(secret_value, salt_hex), expected_hash)
