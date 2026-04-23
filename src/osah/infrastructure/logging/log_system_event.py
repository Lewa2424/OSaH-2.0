import logging

from osah.infrastructure.logging.sanitize_log_message import sanitize_log_message


# ###### ЗАПИС СИСТЕМНОЇ ПОДІЇ У ФАЙЛОВИЙ ЛОГ / SYSTEM FILE LOG EVENT ######
def log_system_event(module_name: str, message_text: str) -> None:
    """Пише службову подію до файлового системного логу без відкритих секретів.
    Writes a service event to the system log without plain secrets.
    """

    logging.getLogger(module_name).info(sanitize_log_message(message_text))
