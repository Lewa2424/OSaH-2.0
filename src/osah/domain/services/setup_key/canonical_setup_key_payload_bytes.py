import json
from typing import Any


# ###### КАНОНІЧНІ БАЙТИ PAYLOAD КЛЮЧА / CANONICAL SETUP KEY PAYLOAD BYTES ######
def canonical_setup_key_payload_bytes(payload: dict[str, Any]) -> bytes:
    """Перетворює payload ключа установки у канонічний UTF-8 JSON для підпису.
    Converts setup key payload into canonical UTF-8 JSON for signing.
    """

    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
