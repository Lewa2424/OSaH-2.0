from sqlite3 import Connection

from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.domain.entities.port_site_risk import PortSiteRisk


# ###### СПИСОК РИЗИКІВ ПАСПОРТА ПОРТ-Р / LIST PORT-R PASSPORT RISKS ######
def list_port_site_risks_for_passport(
    connection: Connection,
    passport_id: int,
) -> tuple[PortSiteRisk, ...]:
    """Повертає всі ризики, прив'язані до паспорта ділянки.
    Returns all risks attached to a site passport.
    """

    rows = connection.execute(
        """
        SELECT
            id,
            passport_id,
            registry_risk_id,
            risk_situation,
            hazard_source,
            occurrence_conditions,
            consequences,
            assessment_reason,
            risk_level,
            method_note,
            inspector_comment,
            suggestion_reason,
            status,
            addition_source,
            sort_order
        FROM port_site_risks
        WHERE passport_id = ?
        ORDER BY sort_order ASC, id ASC;
        """,
        (passport_id,),
    ).fetchall()

    return tuple(
        PortSiteRisk(
            risk_id=int(row["id"]),
            passport_id=int(row["passport_id"]),
            registry_risk_id=int(row["registry_risk_id"]) if row["registry_risk_id"] is not None else None,
            risk_situation=str(row["risk_situation"] or ""),
            hazard_source=str(row["hazard_source"] or ""),
            occurrence_conditions=str(row["occurrence_conditions"] or ""),
            consequences=str(row["consequences"] or ""),
            assessment_reason=str(row["assessment_reason"] or ""),
            risk_level=str(row["risk_level"] or ""),
            method_note=str(row["method_note"] or ""),
            inspector_comment=str(row["inspector_comment"] or ""),
            suggestion_reason=str(row["suggestion_reason"] or ""),
            status=_parse_status(row["status"]),
            addition_source=str(row["addition_source"] or "manual"),
            sort_order=int(row["sort_order"] or 0),
        )
        for row in rows
    )


def _parse_status(value: object) -> PortPassportRiskStatus:
    try:
        return PortPassportRiskStatus(str(value or PortPassportRiskStatus.MANUAL.value))
    except ValueError:
        return PortPassportRiskStatus.MANUAL
