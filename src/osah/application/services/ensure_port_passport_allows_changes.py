from sqlite3 import Connection

from osah.domain.entities.port_passport_status import PortPassportStatus


def ensure_port_passport_allows_changes(connection: Connection, passport_id: int) -> None:
    """Перевіряє, що паспорт існує і не перебуває в архіві.
    Verifies that a passport exists and is not archived.
    """

    row = connection.execute(
        "SELECT status FROM port_site_passports WHERE id = ?;",
        (passport_id,),
    ).fetchone()
    if row is None:
        raise ValueError("Паспорт не знайдено.")
    if str(row["status"] or "") == PortPassportStatus.ARCHIVED.value:
        raise ValueError("Архівний паспорт не можна змінювати.")


def ensure_risk_passport_allows_changes(connection: Connection, risk_id: int) -> int:
    """Повертає passport_id ризику після перевірки, що паспорт не архівний.
    Returns the risk passport_id after verifying that the passport is not archived.
    """

    row = connection.execute(
        """
        SELECT p.id AS passport_id, p.status AS passport_status
        FROM port_site_risks r
        JOIN port_site_passports p ON p.id = r.passport_id
        WHERE r.id = ?;
        """,
        (risk_id,),
    ).fetchone()
    if row is None:
        raise ValueError("Ризик не знайдено.")
    if str(row["passport_status"] or "") == PortPassportStatus.ARCHIVED.value:
        raise ValueError("Архівний паспорт не можна змінювати.")
    return int(row["passport_id"])
