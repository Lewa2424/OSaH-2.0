from pathlib import Path

from osah.domain.entities.port_risk_suggestion import PortRiskSuggestion
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_port_risk_suggestions_for_passport import (
    list_port_risk_suggestions_for_passport,
)


# ###### ЗАВАНТАЖЕННЯ РЕКОМЕНДОВАНИХ РИЗИКІВ ПОРТ-Р / LOAD PORT-R RISK SUGGESTIONS ######
def load_port_risk_suggestions_for_passport(
    database_path: Path,
    passport_id: int,
    *,
    min_score: int = 2,
    limit: int = 100,
) -> tuple[PortRiskSuggestion, ...]:
    """Завантажує рекомендовані ризики для паспорта ділянки.
    Loads suggested risks for a site passport.
    """

    connection = create_database_connection(database_path)
    try:
        return list_port_risk_suggestions_for_passport(
            connection,
            passport_id,
            min_score=min_score,
            limit=limit,
        )
    finally:
        connection.close()
