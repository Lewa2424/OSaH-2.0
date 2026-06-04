import base64
import ctypes
import sys
from ctypes import wintypes


_DPAPI_PREFIX = "dpapi:v1:"
_CRYPTPROTECT_UI_FORBIDDEN = 0x1


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _bytes_to_blob(raw_bytes: bytes) -> _DATA_BLOB:
    buffer = ctypes.create_string_buffer(raw_bytes, len(raw_bytes))
    return _DATA_BLOB(len(raw_bytes), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))


def _blob_to_bytes(blob: _DATA_BLOB) -> bytes:
    return ctypes.string_at(blob.pbData, blob.cbData)


# ###### ЗАХИСТ СЕКРЕТУ ЧЕРЕЗ DPAPI / PROTECT SECRET WITH DPAPI ######
def protect_secret_with_windows_dpapi(secret_value: str) -> str:
    """Шифрує секрет для поточного користувача Windows і повертає маркований рядок.
    Encrypts a secret for the current Windows user and returns a marked string.
    """

    if not sys.platform.startswith("win"):
        raise OSError("DPAPI доступний лише на Windows.")
    if not secret_value:
        return ""

    plain_bytes = secret_value.encode("utf-8")
    input_blob = _bytes_to_blob(plain_bytes)
    output_blob = _DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(input_blob),
        None,
        None,
        None,
        None,
        _CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(output_blob),
    ):
        raise OSError("Не вдалося зашифрувати секрет через DPAPI.")
    protected_bytes = _blob_to_bytes(output_blob)
    ctypes.windll.kernel32.LocalFree(output_blob.pbData)
    return f"{_DPAPI_PREFIX}{base64.b64encode(protected_bytes).decode('ascii')}"


# ###### РОЗШИФРУВАННЯ СЕКРЕТУ ЧЕРЕЗ DPAPI / UNPROTECT SECRET WITH DPAPI ######
def unprotect_secret_with_windows_dpapi(protected_value: str) -> str:
    """Розшифровує секрет, збережений через protect_secret_with_windows_dpapi.
    Decrypts a secret stored via protect_secret_with_windows_dpapi.
    """

    if not protected_value:
        return ""
    if not protected_value.startswith(_DPAPI_PREFIX):
        return protected_value

    if not sys.platform.startswith("win"):
        raise OSError("DPAPI доступний лише на Windows.")

    protected_bytes = base64.b64decode(protected_value.removeprefix(_DPAPI_PREFIX).encode("ascii"))
    input_blob = _bytes_to_blob(protected_bytes)
    output_blob = _DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(input_blob),
        None,
        None,
        None,
        None,
        _CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(output_blob),
    ):
        raise OSError("Не вдалося розшифрувати секрет через DPAPI.")
    plain_bytes = _blob_to_bytes(output_blob)
    ctypes.windll.kernel32.LocalFree(output_blob.pbData)
    return plain_bytes.decode("utf-8")
