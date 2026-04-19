import logging


# ###### ЗАПИС ALERT-ПОДІЇ У ФАЙЛОВИЙ ЛОГ / ЗАПИСЬ ALERT-СОБЫТИЯ В ФАЙЛОВЫЙ ЛОГ ######
def log_alert_event(module_name: str, message_text: str) -> None:
    """Пише критичну alert-подію до файлового системного логу.
    Пишет критичное alert-событие в файловый системный лог.
    """

    logging.getLogger(module_name).warning(f"ALERT | {message_text}")
