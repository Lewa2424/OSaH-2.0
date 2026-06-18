from osah.application.services.ai.build_ai_unified_system_prompt import is_write_command_text
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_track import AiCommandTrack
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.detect_ai_command_track import detect_ai_command_track


def classify_ai_resolution_track(command_text: str) -> AiCommandTrack | None:
    """Класифікує команду для маршрутизації read/nav vs write/bulk.
    Classifies a command for read/nav vs write/bulk routing.
    """

    normalized = command_text.strip()
    if not normalized:
        return None
    if is_write_command_text(normalized):
        return AiCommandTrack.WRITE
    probe = AiCommandDraft(intent=AiIntentKind.UNKNOWN, raw_command=normalized, source="probe")
    return detect_ai_command_track(probe)


def is_write_resolution_track(command_text: str) -> bool:
    """Перевіряє, чи команда належить write/bulk треку.
    Checks whether the command belongs to the write/bulk track.
    """

    return classify_ai_resolution_track(command_text) == AiCommandTrack.WRITE
