from dataclasses import dataclass


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
