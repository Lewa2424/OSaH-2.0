import hashlib


SERVICE_RESET_PEPPER = "OSAH2_SERVICE_RESET_V1"


# ###### ПОБУДОВА СЕРВІСНОГО КОДУ СКИДАННЯ / ПОСТРОЕНИЕ СЕРВИСНОГО КОДА СБРОСА ######
def build_service_reset_code(installation_id: str, request_counter: int) -> str:
    """Будує одноразовий сервісний код для конкретної установки і номера запиту.
    Строит одноразовый сервисный код для конкретной установки и номера запроса.
    """

    digest = hashlib.sha256(
        f"{SERVICE_RESET_PEPPER}|{installation_id}|{request_counter}|v1".encode("utf-8")
    ).hexdigest().upper()
    return f"{digest[:4]}-{digest[4:8]}-{digest[8:12]}"
