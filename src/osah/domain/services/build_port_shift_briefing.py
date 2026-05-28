from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.domain.entities.port_risk_level import PortRiskLevel
from osah.domain.entities.port_shift_briefing import (
    PortShiftBriefing,
    PortShiftBriefingBarrier,
    PortShiftBriefingRisk,
)
from osah.domain.entities.port_site_passport_input import PortSitePassportInput
from osah.domain.entities.port_site_passport_row import PortSitePassportRow
from osah.domain.entities.port_site_risk import PortSiteRisk


_MAX_KEY_RISKS: int = 5
_ACTIVE_RISK_STATUSES: frozenset[PortPassportRiskStatus] = frozenset(
    {PortPassportRiskStatus.ACCEPTED, PortPassportRiskStatus.MANUAL}
)


# ###### ЗБИРАННЯ ДАНИХ ОПЕРАТИВНОГО ЛИСТА ЗМІНИ / BUILD SHIFT BRIEFING DATA ######
def build_port_shift_briefing(
    passport_row: PortSitePassportRow,
    passport_input: PortSitePassportInput,
    risks: tuple[PortSiteRisk, ...],
) -> PortShiftBriefing:
    """Складає dataclass для оперативного листа зміни на основі паспорта і ризиків.
    Builds the dataclass for the shift briefing based on the passport and its risks.
    """

    key_risks = _select_key_risks(risks)
    barriers = _build_barriers(passport_input)
    return PortShiftBriefing(
        passport_code=passport_row.passport_code,
        site_name=passport_input.site_name,
        site_location=passport_input.site_location,
        work_kind=passport_input.work_kind,
        typical_operations=passport_input.typical_operations,
        typical_cargo=passport_input.typical_cargo,
        cargo_features=passport_input.cargo_features,
        main_equipment=passport_input.main_equipment,
        lifting_devices=passport_input.lifting_devices,
        final_profile=passport_row.final_profile,
        status=passport_row.status,
        passport_updated_at=passport_row.updated_at,
        key_risks=key_risks,
        barriers=barriers,
    )


def _select_key_risks(risks: tuple[PortSiteRisk, ...]) -> tuple[PortShiftBriefingRisk, ...]:
    active_risks = tuple(risk for risk in risks if PortPassportRiskStatus(risk.status) in _ACTIVE_RISK_STATUSES)
    ordered_risks = sorted(active_risks, key=lambda risk: (_risk_level_order(risk.risk_level), risk.sort_order))
    selected = ordered_risks[:_MAX_KEY_RISKS]
    return tuple(
        PortShiftBriefingRisk(
            risk_situation=risk.risk_situation,
            hazard_source=risk.hazard_source,
            level=_parse_risk_level(risk.risk_level),
        )
        for risk in selected
    )


def _risk_level_order(raw_level: str) -> int:
    level = _parse_risk_level(raw_level)
    if level is None:
        return 99
    priorities = {
        PortRiskLevel.CRITICAL: 0,
        PortRiskLevel.HIGH: 1,
        PortRiskLevel.MEDIUM: 2,
        PortRiskLevel.LOW: 3,
    }
    return priorities[level]


def _parse_risk_level(raw_level: str) -> PortRiskLevel | None:
    normalized = (raw_level or "").strip().lower()
    if not normalized:
        return None
    try:
        return PortRiskLevel(normalized)
    except ValueError:
        return None


def _build_barriers(passport_input: PortSitePassportInput) -> tuple[PortShiftBriefingBarrier, ...]:
    return (
        PortShiftBriefingBarrier(name="Зв'язок", comment=passport_input.communication_barrier),
        PortShiftBriefingBarrier(name="Огородження / зонування", comment=passport_input.fencing_barrier),
        PortShiftBriefingBarrier(name="Сигнальник", comment=""),
        PortShiftBriefingBarrier(name="Освітлення", comment=passport_input.lighting_barrier),
        PortShiftBriefingBarrier(name="ЗІЗ", comment=passport_input.ppe_text),
        PortShiftBriefingBarrier(name="ВЗП / стропи / захвати", comment=passport_input.lifting_devices),
        PortShiftBriefingBarrier(name="Проходи / проїзди", comment=""),
    )
