import base64
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from osah.domain.services.setup_key.canonical_setup_key_payload_bytes import (
    canonical_setup_key_payload_bytes,
)


# ###### ПІДПИС ДОКУМЕНТА КЛЮЧА / SIGN SETUP KEY DOCUMENT ######
def build_setup_key_document(
    payload: dict[str, Any],
    private_key_path: Path,
) -> dict[str, Any]:
    """Підписує payload ключа установки приватним ключем Ed25519.
    Signs setup key payload with an Ed25519 private key.
    """

    private_key = serialization.load_pem_private_key(
        private_key_path.read_bytes(),
        password=None,
    )
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError("Expected an Ed25519 private key.")

    payload_bytes = canonical_setup_key_payload_bytes(payload)
    signature = private_key.sign(payload_bytes)
    return {
        "payload": payload,
        "signature": base64.b64encode(signature).decode("ascii"),
        "signature_algorithm": "Ed25519",
    }
