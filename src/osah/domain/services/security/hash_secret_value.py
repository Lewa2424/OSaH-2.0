import hashlib


PBKDF2_ITERATION_COUNT = 200_000


# ###### ХЕШУВАННЯ СЕКРЕТНОГО ЗНАЧЕННЯ / ХЕШИРОВАНИЕ СЕКРЕТНОГО ЗНАЧЕНИЯ ######
def hash_secret_value(secret_value: str, salt_hex: str) -> str:
    """Обчислює pbkdf2-hash для пароля або recovery-коду.
    Вычисляет pbkdf2-hash для пароля или recovery-кода.
    """

    return hashlib.pbkdf2_hmac(
        "sha256",
        secret_value.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ITERATION_COUNT,
    ).hex()
