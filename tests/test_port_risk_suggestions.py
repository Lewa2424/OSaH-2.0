import tempfile
import unittest
from pathlib import Path

from osah.application.services.sync_port_passport_tags import sync_port_passport_tags
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_port_risk_suggestions_for_passport import (
    list_port_risk_suggestions_for_passport,
)
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema


class PortRiskSuggestionsTests(unittest.TestCase):
    def test_sync_tags_and_build_suggestions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "osah.db"
            connection = create_database_connection(database_path)
            try:
                ensure_core_schema(connection)
                passport_id = _insert_passport(connection)
                registry_risk_id = _insert_registry_risk(connection)
                _insert_manual_tags(connection)
                _link_risk_with_tags(connection, registry_risk_id)

                synced_count = sync_port_passport_tags(connection, passport_id)
                suggestions = list_port_risk_suggestions_for_passport(connection, passport_id, min_score=1)

                self.assertGreater(synced_count, 0)
                self.assertEqual(len(suggestions), 1)
                self.assertEqual(suggestions[0].registry_risk_id, registry_risk_id)
                self.assertGreaterEqual(suggestions[0].score, 1)
                self.assertIn("Збіг тегів", suggestions[0].suggestion_reason)
            finally:
                connection.close()

    def test_suggestions_skip_already_added_risks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "osah.db"
            connection = create_database_connection(database_path)
            try:
                ensure_core_schema(connection)
                passport_id = _insert_passport(connection)
                registry_risk_id = _insert_registry_risk(connection)
                _insert_manual_tags(connection)
                _link_risk_with_tags(connection, registry_risk_id)
                sync_port_passport_tags(connection, passport_id)
                connection.execute(
                    """
                    INSERT INTO port_site_risks (passport_id, registry_risk_id, risk_situation, status)
                    VALUES (?, ?, ?, 'suggested');
                    """,
                    (passport_id, registry_risk_id, "тестовий ризик"),
                )

                suggestions = list_port_risk_suggestions_for_passport(connection, passport_id, min_score=1)
                self.assertEqual(suggestions, ())
            finally:
                connection.close()


def _insert_passport(connection: object) -> int:
    cursor = connection.execute(
        """
        INSERT INTO port_site_passports (
            passport_code,
            site_name,
            site_description,
            main_equipment
        )
        VALUES (?, ?, ?, ?);
        """,
        (
            "PORT-1",
            "Ділянка навантаження",
            "Працівник перебуває в зоні руху навантажувача.",
            "Навантажувач фронтальний",
        ),
    )
    return int(cursor.lastrowid)


def _insert_registry_risk(connection: object) -> int:
    cursor = connection.execute(
        """
        INSERT INTO port_risk_registry (
            risk_code,
            level_1,
            level_2,
            level_3,
            risk_situation,
            hazard_source,
            occurrence_conditions,
            consequences,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            "1.1.1",
            "Рух техніки",
            "Рух навантажувачів",
            "1.1.1 Перебування працівника в зоні руху",
            "Перебування працівника в зоні руху навантажувача",
            "Навантажувач",
            "Складський майданчик",
            "Травмування",
            "",
        ),
    )
    return int(cursor.lastrowid)


def _insert_manual_tags(connection: object) -> None:
    connection.executemany(
        """
        INSERT INTO port_risk_tags (tag_code, label_uk)
        VALUES (?, ?);
        """,
        (
            ("навантажувач", "навантажувач"),
            ("зон рух", "зоні руху"),
            ("працівник", "працівник"),
        ),
    )


def _link_risk_with_tags(connection: object, registry_risk_id: int) -> None:
    tag_rows = connection.execute(
        "SELECT id FROM port_risk_tags WHERE tag_code IN ('навантажувач', 'зон рух', 'працівник');"
    ).fetchall()
    connection.executemany(
        """
        INSERT INTO port_risk_registry_tags (registry_risk_id, tag_id)
        VALUES (?, ?);
        """,
        ((registry_risk_id, int(tag_row["id"])) for tag_row in tag_rows),
    )


if __name__ == "__main__":
    unittest.main()
