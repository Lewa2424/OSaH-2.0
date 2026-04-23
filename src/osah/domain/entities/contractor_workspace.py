from dataclasses import dataclass

from osah.domain.entities.contractor_record import ContractorRecord


@dataclass(slots=True)
class ContractorWorkspace:
    """Prepared contractors data for ContractorsScreen."""

    records: tuple[ContractorRecord, ...]
