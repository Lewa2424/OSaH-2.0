from dataclasses import dataclass
from pathlib import Path

from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.medical_record import MedicalRecord


@dataclass(slots=True, frozen=True)
class ResolvedAiRecordTarget:
    """Знайдений запис для update-intent.
    Resolved record target for update intents.
    """

    record_id: int
    ppe_record: PpeRecord | None = None
    training_record: TrainingRecord | None = None
    medical_record: MedicalRecord | None = None


def resolve_ai_record_for_update(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    personnel_number: str,
) -> ResolvedAiRecordTarget | None:
    """Знаходить запис для точкового оновлення.
    Finds a record for a point update intent.
    """

    if draft.record_id is not None:
        return _resolve_by_record_id(database_path, draft, draft.record_id, personnel_number)

    if draft.intent == AiIntentKind.UPDATE_PPE_RECORD:
        return _resolve_ppe_record(database_path, draft, personnel_number)
    if draft.intent == AiIntentKind.UPDATE_TRAINING_RECORD:
        return _resolve_training_record(database_path, draft, personnel_number)
    if draft.intent == AiIntentKind.UPDATE_MEDICAL_RECORD:
        return _resolve_medical_record(database_path, personnel_number)
    return None


def _resolve_by_record_id(
    database_path: Path,
    draft: AiCommandDraft,
    record_id: int,
    personnel_number: str,
) -> ResolvedAiRecordTarget | None:
    if draft.intent == AiIntentKind.UPDATE_PPE_RECORD:
        for record in load_ppe_registry(database_path):
            if record.record_id == record_id and record.employee_personnel_number == personnel_number:
                return ResolvedAiRecordTarget(record_id=record_id, ppe_record=record)
    if draft.intent == AiIntentKind.UPDATE_TRAINING_RECORD:
        for record in load_training_registry(database_path):
            if record.record_id == record_id and record.employee_personnel_number == personnel_number:
                return ResolvedAiRecordTarget(record_id=record_id, training_record=record)
    if draft.intent == AiIntentKind.UPDATE_MEDICAL_RECORD:
        for record in load_medical_registry(database_path):
            if record.record_id == record_id and record.employee_personnel_number == personnel_number:
                return ResolvedAiRecordTarget(record_id=record_id, medical_record=record)
    return None


def _resolve_ppe_record(database_path: Path, draft: AiCommandDraft, personnel_number: str) -> ResolvedAiRecordTarget | None:
    item_query = (draft.ppe_item_query or (draft.items[0].name if draft.items else "")).strip()
    if not item_query:
        return None
    candidates = {name.lower() for name in search_ppe_catalog_candidates(database_path, item_query)}
    matches = [
        record
        for record in load_ppe_registry(database_path)
        if record.employee_personnel_number == personnel_number and record.ppe_name.strip().lower() in candidates
    ]
    if len(matches) != 1 or matches[0].record_id is None:
        return None
    return ResolvedAiRecordTarget(record_id=int(matches[0].record_id), ppe_record=matches[0])


def _resolve_training_record(database_path: Path, draft: AiCommandDraft, personnel_number: str) -> ResolvedAiRecordTarget | None:
    training_type = (draft.training_type or "repeated").strip().lower()
    matches = [
        record
        for record in load_training_registry(database_path)
        if record.employee_personnel_number == personnel_number and record.training_type.value == training_type
    ]
    if not matches:
        matches = [
            record
            for record in load_training_registry(database_path)
            if record.employee_personnel_number == personnel_number
        ]
    if len(matches) != 1 or matches[0].record_id is None:
        return None
    return ResolvedAiRecordTarget(record_id=int(matches[0].record_id), training_record=matches[0])


def _resolve_medical_record(database_path: Path, personnel_number: str) -> ResolvedAiRecordTarget | None:
    matches = [record for record in load_medical_registry(database_path) if record.employee_personnel_number == personnel_number]
    if len(matches) != 1 or matches[0].record_id is None:
        return None
    return ResolvedAiRecordTarget(record_id=int(matches[0].record_id), medical_record=matches[0])
