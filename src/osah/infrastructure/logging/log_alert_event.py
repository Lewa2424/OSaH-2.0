import logging

from osah.infrastructure.logging.sanitize_log_message import sanitize_log_message


# ###### ЗАПИС ALERT-ПОДІЇ У ФАЙЛОВИЙ ЛОГ / ALERT FILE LOG EVENT ######
def log_alert_event(module_name: str, message_text: str) -> None:
    """Пише критичну alert-подію до файлового системного логу без відкритих секретів.
    Writes an alert event to the system log without plain secrets.
    """

    logging.getLogger(module_name).warning(f"ALERT | {sanitize_log_message(message_text)}")
