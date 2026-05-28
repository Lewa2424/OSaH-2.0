import tempfile
import unittest
from pathlib import Path

from osah.application.services.add_port_risk_suggestion_to_passport import add_port_risk_suggestion_to_passport
from osah.domain.entities.access_role import AccessRole
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema


class AddPortRiskSuggestionToPassportTests(unittest.TestCase):
    def test_adds_suggested_risk_to_passport(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "osah.db"
            connection = create_database_connection(database_path)
            try:
                ensure_core_schema(connection)
                passport_id = _insert_passport(connection, "PORT-1")
                registry_risk_id = _insert_registry_risk(connection, "1.1.1")
                connection.commit()
            finally:
                connection.close()

            inserted_id = add_port_risk_suggestion_to_passport(
                database_path,
                passport_id,
                registry_risk_id,
                suggestion_reason="Збіг тегів: навантажувач",
                access_role=AccessRole.INSPECTOR,
            )
            self.assertGreater(inserted_id, 0)

            check_connection = create_database_connection(database_path)
            try:
                row = check_connection.execute(
                    """
                    SELECT registry_risk_id, status, addition_source, suggestion_reason
                    FROM port_site_risks
                    WHERE id = ?;
                    """,
                    (inserted_id,),
                ).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(int(row["registry_risk_id"]), registry_risk_id)
                self.assertEqual(str(row["status"]), "suggested")
                self.assertEqual(str(row["addition_source"]), "registry")
            finally:
                check_connection.close()

    def test_returns_existing_record_when_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "osah.db"
            connection = create_database_connection(database_path)
            try:
                ensure_core_schema(connection)
                passport_id = _insert_passport(connection, "PORT-2")
                registry_risk_id = _insert_registry_risk(connection, "1.1.2")
                cursor = connection.execute(
                    """
                    INSERT INTO port_site_risks (
                        passport_id,
                        registry_risk_id,
                        risk_situation,
                        status,
                        addition_source
                    )
                    VALUES (?, ?, ?, 'suggested', 'registry');
                    """,
                    (passport_id, registry_risk_id, "Ризик"),
                )
                existing_id = int(cursor.lastrowid)
                connection.commit()
            finally:
                connection.close()

            returned_id = add_port_risk_suggestion_to_passport(
                database_path,
                passport_id,
                registry_risk_id,
                suggestion_reason="Збіг тегів",
                access_role=AccessRole.INSPECTOR,
            )
            self.assertEqual(returned_id, existing_id)


def _insert_passport(connection: object, passport_code: str) -> int:
    cursor = connection.execute(
        """
        INSERT INTO port_site_passports (passport_code, site_name)
        VALUES (?, ?);
        """,
        (passport_code, "Тестова ділянка"),
    )
    return int(cursor.lastrowid)


def _insert_registry_risk(connection: object, risk_code: str) -> int:
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
            risk_code,
            "Техніка",
            "Рух техніки",
            "Ризик",
            "Ризикова ситуація",
            "Джерело",
            "Умови",
            "Наслідки",
            "",
        ),
    )
    return int(cursor.lastrowid)


if __name__ == "__main__":
    unittest.main()
