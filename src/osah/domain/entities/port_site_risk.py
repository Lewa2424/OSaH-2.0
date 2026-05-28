from dataclasses import dataclass

from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus


@dataclass(slots=True)
class PortSiteRisk:
    """Запис ризику в паспорті виробничої ділянки ПОРТ-Р.
    A risk record within a PORT-R production site passport.
    """

    risk_id: int
    passport_id: int
    registry_risk_id: int | None
    risk_situation: str
    hazard_source: str
    occurrence_conditions: str
    consequences: str
    assessment_reason: str
    risk_level: str
    method_note: str
    inspector_comment: str
    suggestion_reason: str
    status: PortPassportRiskStatus
    addition_source: str
    sort_order: int
