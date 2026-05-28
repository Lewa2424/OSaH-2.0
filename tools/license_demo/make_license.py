"""Create and sign a ClearWork license file for one device.

EN: Build a license payload and sign it with a private key.
RU: Формирует лицензию и подписывает ее приватным ключом.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def parse_args() -> argparse.Namespace:
    """Build command-line arguments.

    EN: Parse CLI arguments for license creation.
    RU: Разбирает аргументы командной строки для создания лицензии.
    """
    parser = argparse.ArgumentParser(description="Create a signed ClearWork license.")
    parser.add_argument(
        "--private-key",
        default="keys/private_key.pem",
        help="Path to private_key.pem",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON payload template",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Path to the resulting license file. If omitted, the file is written to issued/ automatically.",
    )
    parser.add_argument(
        "--issued-dir",
        default="issued",
        help="Directory for generated license files when --output is not provided.",
    )
    return parser.parse_args()


def load_private_key(private_key_path: Path) -> Ed25519PrivateKey:
    """Load the private key from a PEM file.

    EN: Read an Ed25519 private key from PEM.
    RU: Читает приватный ключ Ed25519 из PEM-файла.
    """
    private_key = serialization.load_pem_private_key(
        private_key_path.read_bytes(),
        password=None,
    )
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError("Expected an Ed25519 private key.")
    return private_key


def load_payload(input_path: Path) -> dict[str, Any]:
    """Load a JSON payload template from disk.

    EN: Read license payload data from a JSON file.
    RU: Читает данные полезной нагрузки лицензии из JSON-файла.
    """
    return json.loads(input_path.read_text(encoding="utf-8"))


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    """Convert payload to canonical UTF-8 JSON bytes.

    EN: Normalize payload JSON before signing.
    RU: Нормализует JSON полезной нагрузки перед подписью.
    """
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def create_license_document(
    payload: dict[str, Any],
    private_key: Ed25519PrivateKey,
) -> dict[str, Any]:
    """Create the final signed license document.

    EN: Sign payload bytes and return the final license structure.
    RU: Подписывает полезную нагрузку и возвращает итоговую структуру лицензии.
    """
    payload_bytes = canonical_payload_bytes(payload)
    signature = private_key.sign(payload_bytes)
    return {
        "payload": payload,
        "signature": base64.b64encode(signature).decode("ascii"),
        "signature_algorithm": "Ed25519",
    }


def slugify_text(value: str) -> str:
    """Convert customer text into a filesystem-safe slug.

    EN: Build a simple safe file-name fragment.
    RU: Преобразует текст в безопасный фрагмент имени файла.
    """
    cleaned = re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄєҐґ_-]+", "-", value.strip())
    cleaned = cleaned.strip("-_")
    return cleaned or "customer"


def build_default_output_path(payload: dict[str, Any], issued_dir: Path) -> Path:
    """Build the default output path for a signed license.

    EN: Create a readable file name inside the issued directory.
    RU: Формирует понятное имя файла внутри директории выданных лицензий.
    """
    issued_dir.mkdir(parents=True, exist_ok=True)
    customer_slug = slugify_text(str(payload.get("customer", "customer")))
    device_slug = slugify_text(str(payload.get("device_id", "device")))
    return issued_dir / f"license-{customer_slug}-{device_slug}.json"


def resolve_output_path(
    output_argument: str,
    payload: dict[str, Any],
    issued_dir: Path,
) -> Path:
    """Resolve the final output path for the generated license.

    EN: Choose an explicit output path or create a default path in issued/.
    RU: Выбирает явный путь вывода или создает путь по умолчанию в issued/.
    """
    if output_argument:
        output_path = Path(output_argument).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
    return build_default_output_path(payload, issued_dir.resolve())


def write_license(output_path: Path, license_document: dict[str, Any]) -> None:
    """Write the signed license to disk as formatted JSON.

    EN: Save the final license document as JSON.
    RU: Сохраняет итоговую лицензию в JSON-файл.
    """
    output_path.write_text(
        json.dumps(license_document, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    """Run the license creation flow.

    EN: Entry point for the license generator.
    RU: Точка входа для генератора лицензий.
    """
    args = parse_args()
    private_key_path = Path(args.private_key).resolve()
    input_path = Path(args.input).resolve()
    issued_dir = Path(args.issued_dir).resolve()

    private_key = load_private_key(private_key_path)
    payload = load_payload(input_path)
    license_document = create_license_document(payload, private_key)
    output_path = resolve_output_path(args.output, payload, issued_dir)
    write_license(output_path, license_document)

    print(f"License saved to: {output_path}")


if __name__ == "__main__":
    main()
