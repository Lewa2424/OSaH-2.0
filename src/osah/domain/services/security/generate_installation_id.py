import secrets


# ###### ГЕНЕРАЦІЯ ІДЕНТИФІКАТОРА УСТАНОВКИ / ГЕНЕРАЦИЯ ИДЕНТИФИКАТОРА УСТАНОВКИ ######
def generate_installation_id() -> str:
    """Генерує стабільний ідентифікатор локальної установки.
    Генерирует стабильный идентификатор локальной установки.
    """

    return f"OSAH-{secrets.token_hex(4).upper()}-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
