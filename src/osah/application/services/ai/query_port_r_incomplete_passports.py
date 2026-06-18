from dataclasses import dataclass
from pathlib import Path

from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import PortRiskProfile, format_port_risk_profile
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_port_site_passport_rows import list_port_site_passport_rows


@dataclass(slots=True, frozen=True)
class PortPassportGapRow:
    """Незаповнений або критичний паспорт PORT-R.
    Incomplete or critical PORT-R passport row.
    """

    passport_code: str
    site_name: str
    status: PortPassportStatus
    profile_label: str
    gap_text: str


def query_port_r_incomplete_passports(database_path: Path) -> tuple[PortPassportGapRow, ...]:
    """Повертає паспорти PORT-R з прогалинами або критичним профілем.
    Returns PORT-R passports with gaps or critical profiles.
    """

    connection = create_database_connection(database_path)
    try:
        rows = list_port_site_passport_rows(connection)
    finally:
        connection.close()

    result: list[PortPassportGapRow] = []
    for row in rows:
        profile = row.final_profile if row.final_profile != PortRiskProfile.NOT_CALCULATED else row.calculated_profile
        gap_text = ""
        if profile == PortRiskProfile.NOT_CALCULATED:
            gap_text = "профіль ризику не розраховано"
        elif profile in {PortRiskProfile.HIGH, PortRiskProfile.CRITICAL}:
            gap_text = "критичний або високий профіль ризику"
        elif row.status == PortPassportStatus.DRAFT:
            gap_text = "паспорт у чернетці"
        elif not row.site_name.strip():
            gap_text = "не заповнено назву ділянки"
        else:
            continue
        result.append(
            PortPassportGapRow(
                passport_code=row.passport_code,
                site_name=row.site_name,
                status=row.status,
                profile_label=format_port_risk_profile(profile),
                gap_text=gap_text,
            )
        )
    return tuple(result)
