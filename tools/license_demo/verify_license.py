"""Verify a signed ClearWork license file.

EN: Verify signature integrity and compare the expected device ID.
RU: Проверяет подпись лицензии и сравнивает ожидаемый device ID.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def parse_args() -> argparse.Namespace:
    """Build command-line arguments.

    EN: Parse CLI arguments for license verification.
    RU: Разбирает аргументы командной строки для проверки лицензии.
    """
    parser = argparse.ArgumentParser(description="Verify a signed ClearWork license.")
    parser.add_argument(
        "--public-key",
        default="keys/public_key.pem",
        help="Path to public_key.pem",
    )
    parser.add_argument("--license", required=True, help="Path to the signed license file")
    parser.add_argument("--device-id", required=True, help="Device ID to compare with the license payload")
    return parser.parse_args()


def load_public_key(public_key_path: Path) -> Ed25519PublicKey:
    """Load the public key from a PEM file.

    EN: Read an Ed25519 public key from PEM.
    RU: Читает публичный ключ Ed25519 из PEM-файла.
    """
    public_key = serialization.load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(public_key, Ed25519PublicKey):
        raise TypeError("Expected an Ed25519 public key.")
    return public_key


def load_license_document(license_path: Path) -> dict[str, Any]:
    """Load the signed license document from disk.

    EN: Read the license JSON structure from a file.
    RU: Читает JSON-структуру лицензии из файла.
    """
    return json.loads(license_path.read_text(encoding="utf-8"))


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    """Convert payload to canonical UTF-8 JSON bytes.

    EN: Normalize payload JSON before signature verification.
    RU: Нормализует JSON полезной нагрузки перед проверкой подписи.
    """
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_signature(
    license_document: dict[str, Any],
    public_key: Ed25519PublicKey,
) -> dict[str, Any]:
    """Verify the digital signature and return the payload.

    EN: Validate license signature and return payload on success.
    RU: Проверяет цифровую подпись лицензии и возвращает payload при успехе.
    """
    payload = license_document["payload"]
    signature = base64.b64decode(license_document["signature"])
    public_key.verify(signature, canonical_payload_bytes(payload))
    return payload


def verify_device_id(payload: dict[str, Any], expected_device_id: str) -> None:
    """Verify that the payload device ID matches the current device ID.

    EN: Compare the expected device ID with the signed payload value.
    RU: Сравнивает ожидаемый device ID со значением в подписанном payload.
    """
    actual_device_id = payload.get("device_id")
    if actual_device_id != expected_device_id:
        raise ValueError(
            f"Device ID mismatch. Expected '{expected_device_id}', got '{actual_device_id}'."
        )


def main() -> None:
    """Run the license verification flow.

    EN: Entry point for the license verifier.
    RU: Точка входа для проверяющего скрипта лицензии.
    """
    args = parse_args()
    public_key = load_public_key(Path(args.public_key).resolve())
    license_document = load_license_document(Path(args.license).resolve())

    try:
        payload = verify_signature(license_document, public_key)
        verify_device_id(payload, args.device_id)
    except InvalidSignature as error:
        raise SystemExit(f"Signature check failed: {error}") from error
    except Exception as error:
        raise SystemExit(f"License validation failed: {error}") from error

    print("License is valid.")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
