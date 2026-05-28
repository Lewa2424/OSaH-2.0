from dataclasses import dataclass

from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import PortRiskProfile


@dataclass(slots=True)
class PortSitePassportRow:
    """Рядок списку паспортів ділянок ПОРТ-Р.
    Row for the PORT-R site passport list.
    """

    passport_id: int
    passport_code: str
    site_name: str
    site_type: str
    final_profile: PortRiskProfile
    calculated_profile: PortRiskProfile
    status: PortPassportStatus
    updated_at: str
