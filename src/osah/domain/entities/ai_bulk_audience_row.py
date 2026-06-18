from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AiBulkAudienceRow:
    """Рядок аудиторії для preview масової дії.
    Single audience row for bulk action preview.
    """

    personnel_number: str
    full_name: str
    warning_text: str = ""
