from dataclasses import dataclass

from osah.domain.entities.contractor_worker import ContractorWorker


@dataclass(slots=True)
class ContractorRecord:
    """Contractor record for staged contractors module."""

    contractor_id: str
    company_name: str
    contact_person: str
    contact_phone: str
    contact_email: str
    activity_status: str
    note_text: str
    enterprise_supervisor: str = ""
    work_scope_text: str = ""
    workers: tuple[ContractorWorker, ...] = ()
