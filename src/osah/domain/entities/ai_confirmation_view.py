from dataclasses import dataclass, field


@dataclass(slots=True)
class AiConfirmationLine:
    """Рядок прев'ю для діалогу підтвердження AI.
    Single preview line for the AI confirmation dialog.
    """

    label: str
    value: str


@dataclass(slots=True)
class AiConfirmationView:
    """Дані для побудови діалогу підтвердження AI-дії.
    Data used to build the AI confirmation dialog.
    """

    title: str
    summary: str
    lines: tuple[AiConfirmationLine, ...] = field(default_factory=tuple)
    needs_confirmation: bool = True
    warning_text: str = ""
