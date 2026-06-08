import tempfile
import unittest
from pathlib import Path

from osah.application.services.security.activate_setup_key import activate_setup_key
from osah.application.services.security.ensure_security_baseline import ensure_security_baseline
from osah.domain.services.setup_key.build_setup_key_document import build_setup_key_document
from osah.domain.services.setup_key.build_setup_key_payload import build_setup_key_payload
from osah.domain.services.setup_key.setup_key_paste_token import encode_setup_key_paste_token
from osah.domain.services.setup_key.verify_setup_key_document import SetupKeyVerificationError
from osah.infrastructure.config.resolve_setup_key_public_key_path import resolve_setup_key_public_key_path
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema

from osah.application.services.security.security_setting_keys import (
    INSTALLATION_ID,
    SETUP_KEY_ACTIVATED,
    SETUP_KEY_CUSTOMER,
)


class SetupKeyActivationTests(unittest.TestCase):
    """Тести активації ключа установки ClearWork.
    Tests for ClearWork setup key activation.
    """

    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self._project_root = Path(self._temporary_directory.name)
        self._database_path = self._project_root / "data" / "osah.sqlite3"
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._private_key_path = (
            Path(__file__).resolve().parents[1]
            / "tools"
            / "clearwork_key_admin"
            / "keys"
            / "private_key.pem"
        )

        connection = create_database_connection(self._database_path)
        try:
            ensure_core_schema(connection)
            connection.commit()
        finally:
            connection.close()
        ensure_security_baseline(self._database_path)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def _read_installation_id(self) -> str:
        connection = create_database_connection(self._database_path)
        try:
            app_settings = list_app_settings(connection)
        finally:
            connection.close()
        return app_settings[INSTALLATION_ID]

    def _build_valid_token(self, installation_id: str, customer: str = "ТОВ Тест") -> str:
        payload = build_setup_key_payload(
            customer=customer,
            installation_id=installation_id,
            key_kind="initial",
        )
        document = build_setup_key_document(payload, self._private_key_path)
        return encode_setup_key_paste_token(document)

    def test_activate_setup_key_stores_activation(self) -> None:
        installation_id = self._read_installation_id()
        token = self._build_valid_token(installation_id)

        customer_name = activate_setup_key(self._database_path, token)
        self.assertEqual(customer_name, "ТОВ Тест")

        connection = create_database_connection(self._database_path)
        try:
            app_settings = list_app_settings(connection)
        finally:
            connection.close()

        self.assertEqual(app_settings[SETUP_KEY_ACTIVATED], "1")
        self.assertEqual(app_settings[SETUP_KEY_CUSTOMER], "ТОВ Тест")

    def test_activate_setup_key_rejects_wrong_installation_id(self) -> None:
        token = self._build_valid_token("OSAH-WRONG-00-00")

        with self.assertRaises(SetupKeyVerificationError):
            activate_setup_key(self._database_path, token)

    def test_verify_setup_key_document_accepts_matching_installation_id(self) -> None:
        from osah.domain.services.setup_key.setup_key_paste_token import decode_setup_key_paste_token
        from osah.domain.services.setup_key.verify_setup_key_document import verify_setup_key_document

        installation_id = self._read_installation_id()
        token = self._build_valid_token(installation_id)
        document = decode_setup_key_paste_token(token)
        payload = verify_setup_key_document(
            document,
            public_key_path=resolve_setup_key_public_key_path(),
            expected_installation_id=installation_id,
        )
        self.assertEqual(payload["installation_id"], installation_id)


if __name__ == "__main__":
    unittest.main()
