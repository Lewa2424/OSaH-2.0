import base64
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from osah.domain.services.setup_key.canonical_setup_key_payload_bytes import (
    canonical_setup_key_payload_bytes,
)


class SetupKeyVerificationError(ValueError):
    """Помилка перевірки ключа установки / Setup key verification error."""


# ###### ПЕРЕВІРКА ДОКУМЕНТА КЛЮЧА / VERIFY SETUP KEY DOCUMENT ######
def verify_setup_key_document(
    document: dict[str, Any],
    *,
    public_key_path: Path,
    expected_installation_id: str,
) -> dict[str, Any]:
    """Перевіряє підпис ключа установки та відповідність ID установки.
    Verifies setup key signature and installation ID match.
    """

    payload = document.get("payload")
    signature_text = document.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature_text, str):
        raise SetupKeyVerificationError("Невірний формат ключа установки.")

    public_key = serialization.load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(public_key, Ed25519PublicKey):
        raise SetupKeyVerificationError("Невірний публічний ключ перевірки.")

    try:
        public_key.verify(
            base64.b64decode(signature_text),
            canonical_setup_key_payload_bytes(payload),
        )
    except InvalidSignature as error:
        raise SetupKeyVerificationError("Невірний ключ установки.") from error

    actual_installation_id = str(payload.get("installation_id", "")).strip()
    expected_normalized = expected_installation_id.strip()
    if actual_installation_id != expected_normalized:
        raise SetupKeyVerificationError("Ключ призначений для іншої установки.")

    product_name = str(payload.get("product", "")).strip()
    if product_name != "ClearWork":
        raise SetupKeyVerificationError("Невірний ключ установки.")

    return payload
