from dataclasses import dataclass


@dataclass(slots=True)
class AiItemDraft:
    """Чернетка предмета/ЗІЗ у команді AI.
    Draft PPE/item entry parsed from an AI command.
    """

    name: str
    quantity: int
