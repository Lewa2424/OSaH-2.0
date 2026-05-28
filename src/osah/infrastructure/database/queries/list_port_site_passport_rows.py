from sqlite3 import Connection

from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.domain.entities.port_site_passport_row import PortSitePassportRow


# ###### СПИСОК ПАСПОРТІВ ПОРТ-Р / LIST PORT-R PASSPORTS ######
def list_port_site_passport_rows(
    connection: Connection,
    *,
    include_archived: bool = False,
) -> tuple[PortSitePassportRow, ...]:
    """Завантажує рядки списку паспортів ділянок ПОРТ-Р.
    Loads rows for the PORT-R site passport list.
    """

    rows = connection.execute(
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
        WHERE (? = 1 OR status != ?)
        ORDER BY updated_at DESC, id DESC;
        """,
        (int(include_archived), PortPassportStatus.ARCHIVED.value),
    ).fetchall()

    return tuple(
        PortSitePassportRow(
            passport_id=int(row["id"]),
            passport_code=str(row["passport_code"] or ""),
            site_name=str(row["site_name"] or ""),
            site_type=str(row["site_type"] or ""),
            calculated_profile=_parse_profile(row["calculated_profile"]),
            final_profile=_parse_profile(row["final_profile"]),
            status=_parse_status(row["status"]),
            updated_at=str(row["updated_at"] or ""),
        )
        for row in rows
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
