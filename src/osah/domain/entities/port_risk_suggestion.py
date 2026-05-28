from dataclasses import dataclass


@dataclass(slots=True)
class PortRiskSuggestion:
    """Запропонований реєстровий ризик для конкретного паспорта.
    Suggested registry risk for a specific passport.
    """

    registry_risk_id: int
    risk_code: str
    risk_situation: str
    hazard_source: str
    occurrence_conditions: str
    consequences: str
    score: int
    matched_tag_labels: tuple[str, ...]
    suggestion_reason: str
