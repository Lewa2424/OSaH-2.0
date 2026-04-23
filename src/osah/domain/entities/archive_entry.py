from dataclasses import dataclass

from osah.domain.entities.archive_entry_type import ArchiveEntryType


@dataclass(slots=True)
class ArchiveEntry:
    """Single archive registry row."""

    entry_key: str
    entry_type: ArchiveEntryType
    title: str
    subtitle: str
    status_label: str
    archived_at_text: str
    reason_text: str
    can_reactivate: bool
