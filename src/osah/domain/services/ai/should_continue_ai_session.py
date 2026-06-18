import re

from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind
from osah.domain.services.ai.ai_relative_date_markers import looks_like_date_answer
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text

_NEW_COMMAND_PATTERN = re.compile(
    r"^\s*(?:"
    r"покажи|показати|открой|відкрий|відкрити|open|"
    r"добавь|додай|выдай|видай|занеси|проведи|обнови|онови|"
    r"продли|продлить|продовж|подовж|"
    r"найди|знайди|собери|збери|подготовь|підготуй|"
    r"что|що|кому|кому\s+не|у\s+кого|хто|сколько|скільки"
    r")\b",
    re.IGNORECASE,
)


def should_continue_ai_session(session: AiCommandSession | None, command_text: str) -> bool:
    """Визначає, чи нове повідомлення слід трактувати як відповідь у межах active AI-session.
    Decides whether a new message should be treated as a reply within the active AI session.
    """

    if session is None:
        return False

    normalized_command = command_text.strip()
    if not normalized_command:
        return True

    if session.missing_slots:
        pending_slot = session.missing_slots[0]
        if pending_slot == AiPendingSlotKind.ISSUE_DATE and looks_like_date_answer(normalized_command):
            return True
        if pending_slot in {
            AiPendingSlotKind.WORK_RISK_CATEGORY,
            AiPendingSlotKind.EMPLOYEE,
            AiPendingSlotKind.PPE_ITEM,
            AiPendingSlotKind.TRAINING_TYPE,
            AiPendingSlotKind.BULK_AUDIENCE,
        } and not _NEW_COMMAND_PATTERN.search(normalized_command):
            return True

    if not _NEW_COMMAND_PATTERN.search(normalized_command):
        return True

    compiled = compile_command_text(normalized_command)
    if compiled is None:
        return True

    if compiled.needs_llm:
        return True

    return compiled.draft.intent == AiIntentKind.UNKNOWN
