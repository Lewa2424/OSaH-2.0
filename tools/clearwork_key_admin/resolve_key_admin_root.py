import sys
from pathlib import Path


# ###### КОРІНЬ KEY ADMIN / KEY ADMIN ROOT ######
def resolve_key_admin_root() -> Path:
    """Повертає робочу директорію mini-програми (поруч з exe або main.py).
    Returns the key admin working directory (next to exe or main.py).
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent
