from sqlite3 import Connection

from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.domain.entities.port_site_passport_row import PortSitePassportRow


# ###### ЗАВАНТАЖЕННЯ РЯДКА ПАСПОРТА ПО ID / SELECT PASSPORT ROW BY ID ######
def select_port_site_passport_row_by_id(
    connection: Connection,
    passport_id: int,
) -> PortSitePassportRow:
    """Завантажує рядок списку паспортів ПОРТ-Р по його ідентифікатору.
    Loads a PORT-R passport list row by its identifier.
    """

    row = connection.execute(
        """
        SELECT
            id,
            passport_code,
            site_name,
            site_type,
            calculated_profile,
            final_profile,
            status,
            updated_at
        FROM port_site_passports
        WHERE id = ?;
        """,
        (passport_id,),
    ).fetchone()
    if row is None:
        raise ValueError("Паспорт не знайдено.")

    return PortSitePassportRow(
        passport_id=int(row["id"]),
        passport_code=str(row["passport_code"] or ""),
        site_name=str(row["site_name"] or ""),
        site_type=str(row["site_type"] or ""),
        calculated_profile=_parse_profile(row["calculated_profile"]),
        final_profile=_parse_profile(row["final_profile"]),
        status=_parse_status(row["status"]),
        updated_at=str(row["updated_at"] or ""),
    )


def _parse_profile(value: object) -> PortRiskProfile:
    try:
        return PortRiskProfile(str(value or PortRiskProfile.NOT_CALCULATED.value))
    except ValueError:
        return PortRiskProfile.NOT_CALCULATED


def _parse_status(value: object) -> PortPassportStatus:
    try:
        return PortPassportStatus(str(value or PortPassportStatus.DRAFT.value))
    except ValueError:
        return PortPassportStatus.DRAFT
