from dataclasses import dataclass, field
from pathlib import Path

from osah.domain.entities.ai_command_draft import AiCommandDraft


@dataclass(slots=True, frozen=True)
class PreflightResult:
    """Результат доменного preflight перед confirm.
    Result of domain preflight before confirmation.
    """

    ok: bool
    enriched_draft: AiCommandDraft
    issues: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
