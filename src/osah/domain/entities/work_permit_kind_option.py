from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkPermitKindOption:
    """Типовий варіант виду наряду-допуску для універсального реєстру.
    Typical work-permit kind option for the universal registry.
    """

    key: str
    label: str
    guidance_text: str
