import re


# ###### ІМ'Я ФАЙЛУ ЗАПИТУ НА КЛЮЧ / SETUP KEY REQUEST DEFAULT FILE NAME ######
def build_setup_key_request_default_file_name(installation_id: str) -> str:
    """Формує безпечне ім'я текстового файлу запиту на ключ установки.
    Builds a safe default file name for the setup key request text file.
    """

    sanitized = re.sub(r"[^0-9A-Za-z_-]+", "-", installation_id.strip()).strip("-")
    if not sanitized:
        sanitized = "installation"
    return f"ClearWork-запит-ключа-{sanitized}.txt"
