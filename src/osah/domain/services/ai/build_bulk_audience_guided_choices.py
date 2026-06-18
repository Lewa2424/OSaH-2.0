from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_bulk_intent
from osah.domain.services.ai.extract_bulk_audience_from_command import has_bulk_marker_in_command
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing

BULK_AUDIENCE_HINT_PREFIX = "__bulk_hint:"

_BULK_HINT_TEMPLATES = {
    "department": "в цеху …",
    "position": "в должности …",
    "permit": "учасникам наряду №…",
}


def needs_bulk_audience_guided_clarify(draft: AiCommandDraft) -> bool:
    """Перевіряє, чи потрібні кнопки уточнення аудиторії для «всем».
    Checks whether guided bulk-audience clarification buttons are needed.
    """

    if not is_ai_bulk_intent(draft.intent):
        return False
    if not has_bulk_marker_in_command(draft.raw_command):
        return False
    spec = draft.bulk_audience_spec
    if spec is None:
        return True
    return not has_bulk_audience_narrowing(spec)


def build_bulk_audience_guided_choices() -> tuple[AiEntityChoice, ...]:
    """Будує кнопки уточнення аудиторії для масової команди без критерія.
    Builds guided audience clarification buttons for bulk commands without criteria.
    """

    return (
        AiEntityChoice(
            choice_id=f"{BULK_AUDIENCE_HINT_PREFIX}department__",
            label="Указать подразделение",
            choice_kind="bulk_audience_hint",
        ),
        AiEntityChoice(
            choice_id=f"{BULK_AUDIENCE_HINT_PREFIX}position__",
            label="Указать должность",
            choice_kind="bulk_audience_hint",
        ),
        AiEntityChoice(
            choice_id=f"{BULK_AUDIENCE_HINT_PREFIX}permit__",
            label="Указать наряд",
            choice_kind="bulk_audience_hint",
        ),
    )


def is_bulk_audience_hint_choice(choice_id: str) -> bool:
    """Перевіряє, чи choice_id — підказка для bulk-аудиторії.
    Checks whether a choice id is a bulk audience hint button.
    """

    return choice_id.startswith(BULK_AUDIENCE_HINT_PREFIX)


def bulk_audience_hint_template(choice_id: str) -> str:
    """Повертає шаблон фрази для обраної підказки аудиторії.
    Returns a phrase template for the selected audience hint.
    """

    kind = choice_id.removeprefix(BULK_AUDIENCE_HINT_PREFIX).removesuffix("__")
    return _BULK_HINT_TEMPLATES.get(kind, "…")
