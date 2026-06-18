from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AiDialogueTurn:
    """Один обмін у чаті AI-асистента.
    A single turn in the AI assistant chat.
    """

    role: str
    text: str
