from dataclasses import dataclass, field

from osah.domain.entities.port_compensating_barrier_item import PortCompensatingBarrierItem
from osah.domain.entities.port_macrovariable_threshold import PortMacrovariableThreshold
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_level import PortRiskLevel
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.domain.entities.port_shift_decision import PortShiftDecision
from osah.domain.entities.port_shift_zone import PortShiftZone


@dataclass(slots=True)
class PortShiftBriefingRisk:
    """Один рядок ключових ризиків для оперативного листа зміни.
    A single key-risks row for the shift briefing.
    """

    risk_situation: str
    hazard_source: str
    level: PortRiskLevel | None


@dataclass(slots=True)
class PortShiftBriefingBarrier:
    """Критичний бар'єр для оперативного листа зміни (стан фіксує лінійний керівник).
    A critical barrier for the shift briefing (the state is recorded by the line manager).
    """

    name: str
    comment: str


@dataclass(slots=True)
class PortShiftBriefing:
    """Дані для генерації оперативного листа зміни на базі паспорта ПОРТ-Р.
    Data for generating the PORT-R shift briefing from a site passport.
    """

    passport_code: str
    site_name: str
    site_location: str
    work_kind: str
    typical_operations: str
    typical_cargo: str
    cargo_features: str
    main_equipment: str
    lifting_devices: str
    final_profile: PortRiskProfile
    status: PortPassportStatus
    passport_updated_at: str
    key_risks: tuple[PortShiftBriefingRisk, ...] = field(default_factory=tuple)
    barriers: tuple[PortShiftBriefingBarrier, ...] = field(default_factory=tuple)
    r_dyn: float | None = None
    zone: PortShiftZone | None = None
    r_base: float = 1.0
    thresholds: tuple[PortMacrovariableThreshold, ...] = field(default_factory=tuple)
    compensating_barriers: tuple[PortCompensatingBarrierItem, ...] = field(default_factory=tuple)
    decision: PortShiftDecision | None = None
    active_barrier_name: str = ""
    triggered_threshold_ids: frozenset[int] = field(default_factory=frozenset)
    is_record_export: bool = False
    record_shift_date: str = ""
