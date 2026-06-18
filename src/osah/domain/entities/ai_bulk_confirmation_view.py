from dataclasses import dataclass, field

from osah.domain.entities.ai_bulk_audience_row import AiBulkAudienceRow


@dataclass(slots=True)
class AiBulkConfirmationView:
    """Дані для діалогу підтвердження масової AI-дії.
    Data used to build the bulk AI confirmation dialog.
    """

    title: str
    summary: str
    action_summary: str
    rows: tuple[AiBulkAudienceRow, ...] = field(default_factory=tuple)
    warning_text: str = ""
