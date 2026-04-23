from dataclasses import dataclass

from osah.domain.entities.archive_entry import ArchiveEntry


@dataclass(slots=True)
class ArchiveWorkspace:
    """Archive workspace prepared for ArchiveScreen."""

    entries: tuple[ArchiveEntry, ...]
