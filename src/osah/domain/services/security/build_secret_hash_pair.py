import secrets

from osah.domain.services.security.hash_secret_value import hash_secret_value


# ###### ПОБУДОВА ПАРИ СІЛЬ ПЛЮС ХЕШ / ПОСТРОЕНИЕ ПАРЫ СОЛЬ ПЛЮС ХЕШ ######
def build_secret_hash_pair(secret_value: str) -> tuple[str, str]:
    """Генерує нову сіль і хеш для секретного значення.
    Генерирует новую соль и хеш для секретного значения.
    """

    salt_hex = secrets.token_hex(16)
    return salt_hex, hash_secret_value(secret_value, salt_hex)
