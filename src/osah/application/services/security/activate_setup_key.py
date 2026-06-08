from datetime import datetime
from pathlib import Path

from osah.domain.services.setup_key.setup_key_paste_token import decode_setup_key_paste_token
from osah.domain.services.setup_key.verify_setup_key_document import (
    SetupKeyVerificationError,
    verify_setup_key_document,
)
from osah.infrastructure.config.resolve_setup_key_public_key_path import resolve_setup_key_public_key_path
from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings

from osah.application.services.security.security_setting_keys import (
    INSTALLATION_ID,
    SETUP_KEY_ACTIVATED,
    SETUP_KEY_ACTIVATED_AT,
    SETUP_KEY_CUSTOMER,
)


# ###### АКТИВАЦІЯ КЛЮЧА УСТАНОВКИ / ACTIVATE SETUP KEY ######
def activate_setup_key(database_path: Path, paste_token: str) -> str:
    """Перевіряє ключ установки та зберігає факт активації в локальній базі.
    Verifies a setup key and stores activation state in the local database.

    Повертає назву підприємства з payload.
    Returns the customer name from the payload.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
        if app_settings.get(SETUP_KEY_ACTIVATED, "0") == "1":
            return app_settings.get(SETUP_KEY_CUSTOMER, "")

        installation_id = app_settings.get(INSTALLATION_ID, "").strip()
        if not installation_id:
            raise SetupKeyVerificationError("ID установки ще не сформовано.")

        document = decode_setup_key_paste_token(paste_token)
        payload = verify_setup_key_document(
            document,
            public_key_path=resolve_setup_key_public_key_path(),
            expected_installation_id=installation_id,
        )
        customer_name = str(payload.get("customer", "")).strip()
        activated_at = datetime.now().isoformat(timespec="seconds")
        upsert_app_settings_batch(
            connection,
            {
                SETUP_KEY_ACTIVATED: "1",
                SETUP_KEY_ACTIVATED_AT: activated_at,
                SETUP_KEY_CUSTOMER: customer_name,
            },
        )
        connection.commit()
        return customer_name
    finally:
        connection.close()
