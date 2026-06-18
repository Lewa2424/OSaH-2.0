import re
from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.detect_ai_command_track import has_today_date_marker, infer_write_module_key
from osah.domain.services.ai.normalize_ai_training_type import infer_ai_training_type_from_command

_CREATE_RECORD_VERB_PATTERN = re.compile(
    r"\b(?:"
    r"занеси|занести|внеси|внести|проведи|провести|"
    r"створи|создай|додай|добавь|оформи|забей|впиши"
    r")\b",
    re.IGNORECASE,
)
_UPDATE_RECORD_VERB_PATTERN = re.compile(
    r"\b(?:"
    r"онови|обнови|зміни|измени|"
    r"продл|продовж|подовж|extend"
    r")\b",
    re.IGNORECASE,
)
_CREATE_INTENT_BY_MODULE = {
    "ppe": AiIntentKind.CREATE_PPE_ISSUANCE,
    "trainings": AiIntentKind.CREATE_TRAINING_RECORD,
    "medical": AiIntentKind.CREATE_MEDICAL_RECORD,
}


def reconcile_write_create_command(draft: AiCommandDraft) -> AiCommandDraft:
    """Перемикає UPDATE на CREATE для фраз «занеси/внеси/проведи …».
    Switches UPDATE intents to CREATE for add/record phrases.
    """

    raw_command = draft.raw_command.strip()
    if not raw_command:
        return draft
    if not _CREATE_RECORD_VERB_PATTERN.search(raw_command):
        return draft
    if _UPDATE_RECORD_VERB_PATTERN.search(raw_command):
        return draft

    module_key = infer_write_module_key(raw_command, draft)
    if module_key is None:
        return draft

    create_intent = _CREATE_INTENT_BY_MODULE.get(module_key)
    if create_intent is None:
        return draft

    updates: dict[str, object] = {
        "intent": create_intent,
        "module_key": module_key,
        "needs_confirmation": True,
    }
    if not draft.issue_date and (has_today_date_marker(raw_command) or _CREATE_RECORD_VERB_PATTERN.search(raw_command)):
        updates["issue_date"] = "сьогодні"

    if module_key == "trainings":
        training_type = infer_ai_training_type_from_command(raw_command) or draft.training_type
        if training_type:
            updates["training_type"] = training_type

    return replace(draft, **updates)
