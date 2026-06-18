from dataclasses import replace
from pathlib import Path

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_preflight_result import PreflightResult
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.ai.detect_duplicate_ppe_issuance import detect_duplicate_ppe_issuance
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type
from osah.domain.services.find_training_chronology_conflict_reason import find_training_chronology_conflict_reason
from osah.domain.services.parse_service_date_text import parse_service_date_text
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_training_records import list_training_records


def preflight_ai_command_draft(
    draft: AiCommandDraft,
    *,
    database_path: Path | None = None,
    resolved_personnel_number: str | None = None,
) -> PreflightResult:
    """Доменний dry-run перед confirm: обчислює слоти і перевіряє блокери.
    Domain dry-run before confirm: computes slots and checks blockers.
    """

    if draft.intent == AiIntentKind.CREATE_TRAINING_RECORD:
        return _preflight_create_training(draft, database_path, resolved_personnel_number)
    if draft.intent == AiIntentKind.CREATE_PPE_ISSUANCE:
        return _preflight_create_ppe(draft, database_path, resolved_personnel_number)
    if draft.intent == AiIntentKind.CREATE_MEDICAL_RECORD:
        return _preflight_create_medical(draft)
    if draft.intent.value.startswith("bulk_"):
        return _preflight_bulk(draft)
    if draft.intent == AiIntentKind.QUERY_MODULE_STATUS:
        return PreflightResult(ok=True, enriched_draft=draft)

    return PreflightResult(ok=True, enriched_draft=draft)


def _preflight_create_training(
    draft: AiCommandDraft,
    database_path: Path | None,
    resolved_personnel_number: str | None,
) -> PreflightResult:
    issues: list[str] = []
    warnings: list[str] = []
    enriched = draft

    training_type = TrainingType(normalize_ai_training_type(draft.training_type))
    work_risk = TrainingWorkRiskCategory((draft.work_risk_category or "not_applicable").strip() or "not_applicable")

    if not draft.issue_date:
        issues.append("Потрібна дата інструктажу.")
        return PreflightResult(ok=False, enriched_draft=enriched, issues=tuple(issues))

    try:
        event_date = parse_service_date_text(normalize_ai_issue_date_text(draft.issue_date))
    except ValueError as error:
        return PreflightResult(ok=False, enriched_draft=enriched, issues=(str(error),))

    manual_next = None
    if draft.next_control_date:
        try:
            manual_next = parse_service_date_text(normalize_ai_issue_date_text(draft.next_control_date))
        except ValueError as error:
            return PreflightResult(ok=False, enriched_draft=enriched, issues=(str(error),))

    try:
        next_control_iso, _, resolved_risk = resolve_training_next_control_date(
            training_type,
            event_date,
            TrainingPersonCategory.OWN_EMPLOYEE,
            True,
            work_risk,
            manual_next,
            False,
            draft.use_manual_next_control_date,
        )
    except ValueError as error:
        return PreflightResult(ok=False, enriched_draft=enriched, issues=(str(error),))

    enriched = replace(
        enriched,
        next_control_date=next_control_iso or enriched.next_control_date,
        work_risk_category=resolved_risk.value,
    )

    personnel_number = (resolved_personnel_number or draft.personnel_number or "").strip()
    if database_path is not None and personnel_number:
        connection = create_database_connection(database_path)
        try:
            existing = tuple(
                record
                for record in list_training_records(connection)
                if record.employee_personnel_number == personnel_number
            )
            from osah.domain.entities.training_record import TrainingRecord
            from osah.domain.entities.training_status import TrainingStatus

            preview = TrainingRecord(
                record_id=None,
                employee_personnel_number=personnel_number,
                employee_full_name="",
                training_type=training_type,
                event_date=event_date.isoformat(),
                next_control_date=next_control_iso,
                conducted_by=(draft.conducted_by or "Інспектор").strip(),
                note_text="",
                status=TrainingStatus.CURRENT,
                work_risk_category=resolved_risk,
            )
            conflict = find_training_chronology_conflict_reason(preview, existing)
            if conflict:
                warnings.append(conflict)
        finally:
            connection.close()

    return PreflightResult(ok=not issues, enriched_draft=enriched, issues=tuple(issues), warnings=tuple(warnings))


def _preflight_create_ppe(
    draft: AiCommandDraft,
    database_path: Path | None,
    resolved_personnel_number: str | None,
) -> PreflightResult:
    warnings: list[str] = []
    personnel_number = (resolved_personnel_number or draft.personnel_number or "").strip()
    if database_path is not None and personnel_number:
        for item in draft.items:
            if detect_duplicate_ppe_issuance(
                database_path,
                personnel_number=personnel_number,
                ppe_name=item.name,
                issue_date_text=draft.issue_date,
            ):
                warnings.append("Схожий запис ЗІЗ уже існує.")
                break
    return PreflightResult(ok=True, enriched_draft=draft, warnings=tuple(warnings))


def _preflight_create_medical(draft: AiCommandDraft) -> PreflightResult:
    if not draft.issue_date:
        return PreflightResult(ok=False, enriched_draft=draft, issues=("Потрібна дата медогляду.",))
    return PreflightResult(ok=True, enriched_draft=draft)


def _preflight_bulk(draft: AiCommandDraft) -> PreflightResult:
    spec = draft.bulk_audience_spec
    if spec is None or not has_bulk_audience_narrowing(spec):
        return PreflightResult(
            ok=False,
            enriched_draft=draft,
            issues=("Уточніть аудиторію для групової операції.",),
        )
    return PreflightResult(ok=True, enriched_draft=draft)
