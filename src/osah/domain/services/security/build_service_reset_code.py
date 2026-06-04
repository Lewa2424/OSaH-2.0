import hashlib
import hmac


# ###### ПОБУДОВА СЕРВІСНОГО КОДУ СКИДАННЯ / ПОСТРОЕНИЕ СЕРВИСНОГО КОДА СБРОСА ######
def build_service_reset_code(installation_id: str, request_counter: int, service_reset_secret: str) -> str:
    """Будує одноразовий сервісний код для конкретної установки і номера запиту.
    Строит одноразовый сервисный код для конкретной установки и номера запроса.
    """

    normalized_secret = service_reset_secret.strip()
    if not normalized_secret:
        raise ValueError("Сервісний секрет скидання не налаштований.")

    digest = hmac.new(
        normalized_secret.encode("utf-8"),
        f"{installation_id}|{request_counter}|v1".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()
    return f"{digest[:4]}-{digest[4:8]}-{digest[8:12]}"
