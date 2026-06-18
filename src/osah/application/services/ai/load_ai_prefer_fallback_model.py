from pathlib import Path

from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings

AI_PREFER_FALLBACK_MODEL_KEY = "ai.prefer_fallback_model"


def load_ai_prefer_fallback_model(database_path: Path) -> bool:
    """Читає налаштування використання легшої AI-моделі.
    Reads whether the lighter AI model should be preferred.
    """

    connection = create_database_connection(database_path)
    try:
        settings = list_app_settings(connection)
    finally:
        connection.close()
    return settings.get(AI_PREFER_FALLBACK_MODEL_KEY, "0") == "1"
