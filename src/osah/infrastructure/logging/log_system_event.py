import logging


# ###### ЗАПИС СИСТЕМНОЇ ПОДІЇ У ФАЙЛОВИЙ ЛОГ / ЗАПИСЬ СИСТЕМНОГО СОБЫТИЯ В ФАЙЛОВЫЙ ЛОГ ######
def log_system_event(module_name: str, message_text: str) -> None:
    """Пише службову інформаційну подію до файлового системного логу.
    Пишет служебное информационное событие в файловый системный лог.
    """

    logging.getLogger(module_name).info(message_text)
