from pathlib import Path

from osah.application.services.ai.load_ai_prefer_fallback_model import AI_PREFER_FALLBACK_MODEL_KEY
from osah.domain.entities.access_role import AccessRole
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection


def save_ai_prefer_fallback_model(
    database_path: Path,
    *,
    prefer_fallback_model: bool,
    access_role: AccessRole,
) -> None:
    """Зберігає налаштування використання легшої AI-моделі.
    Saves the lighter AI model preference setting.
    """

    ensure_write_access(access_role, "save_ai_prefer_fallback_model")
    connection = create_database_connection(database_path)
    try:
        upsert_app_setting(
            connection,
            AI_PREFER_FALLBACK_MODEL_KEY,
            "1" if prefer_fallback_model else "0",
        )
        connection.commit()
    finally:
        connection.close()
