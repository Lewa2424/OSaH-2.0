import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema
from osah.infrastructure.database.seed.seed_port_risk_registry import seed_port_risk_registry
from osah.infrastructure.database.seed.seed_port_risk_registry_tags import seed_port_risk_registry_tags


class SeedPortRiskRegistryTests(unittest.TestCase):
    """Тести вбудованого seed реєстру ризиків ПОРТ-Р.
    Tests for embedded PORT-R risk registry seeding.
    """

    def test_seed_populates_registry_without_xlsx(self) -> None:
        """На чистій установці без for_data реєстр і теги заповнюються з вбудованого seed.
        On a clean install without for_data the registry and tags are filled from embedded seed.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            application_paths.data_directory.mkdir(parents=True, exist_ok=True)
            missing_xlsx = application_paths.project_root / "for_data" / "Ризики в порту.xlsx"

            connection = create_database_connection(application_paths.database_file_path)
            try:
                ensure_core_schema(connection)
                inserted = seed_port_risk_registry(connection, missing_xlsx)
                seed_port_risk_registry_tags(connection)
                connection.commit()

                registry_total = connection.execute(
                    "SELECT COUNT(*) FROM port_risk_registry;"
                ).fetchone()[0]
                tag_links_total = connection.execute(
                    "SELECT COUNT(*) FROM port_risk_registry_tags;"
                ).fetchone()[0]
            finally:
                connection.close()

            self.assertGreaterEqual(inserted, 306)
            self.assertGreaterEqual(registry_total, 306)
            self.assertGreater(tag_links_total, 0)


if __name__ == "__main__":
    unittest.main()
