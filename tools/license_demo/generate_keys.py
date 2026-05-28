"""Create an Ed25519 key pair for offline license signing.

EN: Generate a private/public key pair for local license signing.
RU: Создает пару приватного и публичного ключей для локальной подписи лицензий.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def parse_args() -> argparse.Namespace:
    """Build command-line arguments.

    EN: Parse CLI arguments for the key generator.
    RU: Разбирает аргументы командной строки для генератора ключей.
    """
    parser = argparse.ArgumentParser(description="Generate an Ed25519 key pair.")
    parser.add_argument(
        "--output-dir",
        default="keys",
        help="Directory where private_key.pem and public_key.pem will be saved.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing private_key.pem and public_key.pem files.",
    )
    return parser.parse_args()


def ensure_overwrite_allowed(output_dir: Path, force: bool) -> None:
    """Check whether existing keys may be overwritten.

    EN: Stop the script if keys already exist and force mode is not enabled.
    RU: Останавливает скрипт, если ключи уже существуют и не указан режим перезаписи.
    """
    private_key_path = output_dir / "private_key.pem"
    public_key_path = output_dir / "public_key.pem"
    if not force and (private_key_path.exists() or public_key_path.exists()):
        raise SystemExit(
            "Keys already exist in the output directory. "
            "Use --force if you really want to overwrite them."
        )


def write_key_pair(output_dir: Path, force: bool) -> None:
    """Generate and save a private/public key pair as PEM files.

    EN: Create Ed25519 keys and write them to PEM files.
    RU: Создает ключи Ed25519 и сохраняет их в PEM-файлы.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_overwrite_allowed(output_dir, force)

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_key_path = output_dir / "private_key.pem"
    public_key_path = output_dir / "public_key.pem"

    private_key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_key_path.write_bytes(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

    print(f"Private key saved to: {private_key_path}")
    print(f"Public key saved to:  {public_key_path}")


def main() -> None:
    """Run the key generation flow.

    EN: Entry point for the key generator script.
    RU: Точка входа для скрипта генерации ключей.
    """
    args = parse_args()
    write_key_pair(Path(args.output_dir).resolve(), force=args.force)


if __name__ == "__main__":
    main()
