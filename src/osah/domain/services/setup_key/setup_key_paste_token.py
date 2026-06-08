import base64
import json
from typing import Any

SETUP_KEY_PASTE_PREFIX = "CW-"


# ###### КОДУВАННЯ КЛЮЧА ДЛЯ ВСТАВКИ / ENCODE SETUP KEY PASTE TOKEN ######
def encode_setup_key_paste_token(document: dict[str, Any]) -> str:
    """Кодує підписаний документ ключа у рядок для вставки користувачем.
    Encodes a signed setup key document into a user paste string.
    """

    encoded = base64.urlsafe_b64encode(
        json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("ascii").rstrip("=")
    return f"{SETUP_KEY_PASTE_PREFIX}{encoded}"


# ###### ДЕКОДУВАННЯ КЛЮЧА З ВСТАВКИ / DECODE SETUP KEY PASTE TOKEN ######
def decode_setup_key_paste_token(paste_token: str) -> dict[str, Any]:
    """Розкодовує рядок ключа установки у підписаний документ.
    Decodes a setup key paste string into a signed document.
    """

    normalized = paste_token.strip()
    if not normalized.startswith(SETUP_KEY_PASTE_PREFIX):
        raise ValueError("Невірний формат ключа установки.")

    encoded_part = normalized[len(SETUP_KEY_PASTE_PREFIX):]
    padding = "=" * ((4 - len(encoded_part) % 4) % 4)
    document_bytes = base64.urlsafe_b64decode(encoded_part + padding)
    document = json.loads(document_bytes.decode("utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Невірний формат ключа установки.")
    return document
