from enum import StrEnum


class AiDispatchResultKind(StrEnum):
    """Вид результата маршрутизации AI-команды после разбора.
    Dispatch result kind for a parsed AI command.
    """

    ANSWER_READY = "answer_ready"
    NAVIGATION_READY = "navigation_ready"
    ENTITY_CHOICES_REQUIRED = "entity_choices_required"
    NOT_FOUND = "not_found"
    WRITE_REQUIRED = "write_required"
    BULK_REQUIRED = "bulk_required"
    UNSUPPORTED = "unsupported"
