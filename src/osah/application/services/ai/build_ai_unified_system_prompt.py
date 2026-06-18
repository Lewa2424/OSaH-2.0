import re

from osah.application.services.ai.build_ai_read_system_prompt import build_ai_read_system_prompt
from osah.application.services.ai.build_ai_semantic_system_prompt import build_ai_semantic_system_prompt

_WRITE_MARKERS = re.compile(
    r"\b(?:"
    r"занеси|занести|видай|выдай|выдать|дай|раздай|"
    r"впиши|выпиши|оформи|проведи|провести|создай|створи|"
    r"додай|добавь|заміни|замени|онови|обнови|переведи|перевести"
    r")\b",
    re.IGNORECASE,
)

_DIALOGUE_COREFERENCE = (
    "Якщо у user prompt є блок [dialogue_context], використовуй його для coreference: "
    "«им/их» = audience_personnel_numbers, імена з follow-up = підмножина audience, "
    "«ему/ей» = last_mentioned_personnel_number."
)


def is_write_command_text(command_text: str | None) -> bool:
    """Перевіряє, чи команда належить до write/bulk треку.
    Checks whether a command belongs to the write/bulk track.
    """

    if command_text is None:
        return True
    return _WRITE_MARKERS.search(command_text.strip()) is not None


def build_ai_unified_system_prompt(command_text: str | None = None) -> str:
    """Повертає system prompt: write → semantic JSON; read/nav → compact legacy.
    Returns system prompt: write → semantic JSON; read/nav → compact legacy.
    """

    if is_write_command_text(command_text):
        blocks = [
            build_ai_semantic_system_prompt(),
            _DIALOGUE_COREFERENCE,
            "Для write/bulk повертай лише semantic JSON (mode, module, audience, payload, conditions).",
            "Приклад multi-turn:",
            '1) "У кого нет каски?" -> read через інший шлях',
            '2) "выдай Лысенко и Петрову" -> create_ppe_issuance, audience.type=employee_list',
            '3) "выдай им каски" -> create_ppe_issuance, audience з dialogue_context',
        ]
        return "\n\n".join(blocks)

    blocks = [
        build_ai_read_system_prompt(),
        _DIALOGUE_COREFERENCE,
        "Для read/nav/explain повертай legacy JSON з intent.",
    ]
    return "\n\n".join(blocks)
