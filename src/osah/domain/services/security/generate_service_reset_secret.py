import secrets


# ###### ГЕНЕРАЦІЯ СЕРВІСНОГО СЕКРЕТУ / GENERATE SERVICE RESET SECRET ######
def generate_service_reset_secret() -> str:
    """Генерує випадковий секрет для побудови сервісних кодів скидання.
    Generates a random secret for building service reset codes.
    """

    return secrets.token_hex(32)
