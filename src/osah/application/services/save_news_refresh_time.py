import re
from pathlib import Path

from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
from osah.infrastructure.database.create_database_connection import create_database_connection


_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


# ###### ЗБЕРЕЖЕННЯ ЧАСУ ПЕРЕВІРКИ НОВИН / SAVE NEWS REFRESH TIME ######
def save_news_refresh_time(database_path: Path, refresh_time: str) -> None:
    """Зберігає щоденний час перевірки новин у налаштуваннях застосунку.
    Сохраняет ежедневное время проверки новостей в настройках приложения.
    """

    normalized = refresh_time.strip()
    if not _TIME_PATTERN.match(normalized):
        raise ValueError("Формат часу має бути HH:MM (наприклад, 08:30).")

    connection = create_database_connection(database_path)
    try:
        upsert_app_settings_batch(connection, {"news.refresh_time": normalized})
        connection.commit()
    finally:
        connection.close()
