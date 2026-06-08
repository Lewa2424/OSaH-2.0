import sys
from pathlib import Path


# ###### ШЛЯХ ДО ПУБЛІЧНОГО КЛЮЧА / SETUP KEY PUBLIC KEY PATH ######
def resolve_setup_key_public_key_path() -> Path:
    """Повертає шлях до вбудованого публічного ключа перевірки ключа установки.
    Returns the path to the embedded setup key verification public key.
    """

    if getattr(sys, "frozen", False):
        base_directory = Path(sys._MEIPASS) / "osah" / "infrastructure" / "config"
    else:
        base_directory = Path(__file__).resolve().parent
    return base_directory / "setup_key_public_key.pem"
