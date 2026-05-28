from sqlite3 import Connection

from osah.domain.entities.port_risk_suggestion import PortRiskSuggestion


# ###### СПИСОК РЕКОМЕНДОВАНИХ РИЗИКІВ ПОРТ-Р / LIST PORT-R RISK SUGGESTIONS ######
def list_port_risk_suggestions_for_passport(
    connection: Connection,
    passport_id: int,
    *,
    min_score: int = 2,
    limit: int = 100,
) -> tuple[PortRiskSuggestion, ...]:
    """Повертає реєстрові ризики, що збіглися з тегами паспорта.
    Returns registry risks matched by passport tags.
    """

    rows = connection.execute(
        """
        SELECT
            r.id AS registry_risk_id,
            r.risk_code AS risk_code,
            r.risk_situation AS risk_situation,
            r.hazard_source AS hazard_source,
            r.occurrence_conditions AS occurrence_conditions,
            r.consequences AS consequences,
            COUNT(*) AS score,
            GROUP_CONCAT(t.label_uk, ', ') AS matched_labels
        FROM port_passport_tags ppt
        JOIN port_risk_registry_tags rrt
            ON rrt.tag_id = ppt.tag_id
        JOIN port_risk_registry r
            ON r.id = rrt.registry_risk_id
        JOIN port_risk_tags t
            ON t.id = ppt.tag_id
        WHERE ppt.passport_id = ?
          AND NOT EXISTS (
              SELECT 1
              FROM port_site_risks psr
              WHERE psr.passport_id = ?
                AND psr.registry_risk_id = r.id
          )
        GROUP BY r.id
        HAVING COUNT(*) >= ?
        ORDER BY score DESC, r.id ASC
        LIMIT ?;
        """,
        (passport_id, passport_id, min_score, limit),
    ).fetchall()

    suggestions: list[PortRiskSuggestion] = []
    for row in rows:
        matched_labels = _split_labels(str(row["matched_labels"] or ""))
        suggestions.append(
            PortRiskSuggestion(
                registry_risk_id=int(row["registry_risk_id"]),
                risk_code=str(row["risk_code"] or ""),
                risk_situation=str(row["risk_situation"] or ""),
                hazard_source=str(row["hazard_source"] or ""),
                occurrence_conditions=str(row["occurrence_conditions"] or ""),
                consequences=str(row["consequences"] or ""),
                score=int(row["score"] or 0),
                matched_tag_labels=matched_labels,
                suggestion_reason=_build_reason(matched_labels),
            )
        )
    return tuple(suggestions)


def _split_labels(raw_labels: str) -> tuple[str, ...]:
    labels = [item.strip() for item in raw_labels.split(",") if item.strip()]
    unique_labels = list(dict.fromkeys(labels))
    return tuple(unique_labels)


def _build_reason(matched_labels: tuple[str, ...]) -> str:
    if not matched_labels:
        return ""
    preview = ", ".join(matched_labels[:5])
    extra_count = len(matched_labels) - 5
    if extra_count > 0:
        return f"Збіг тегів: {preview} (+{extra_count})"
    return f"Збіг тегів: {preview}"
