from dataclasses import dataclass


@dataclass(slots=True)
class ContractorWorker:
    """Працівник підрядника для легкого контролю допуску.
    Contractor worker for lightweight access-readiness control.
    """

    worker_id: str
    full_name: str
    role_name: str
    training_ok: bool
    ppe_ok: bool
    medical_ok: bool
    access_ok: bool
    note_text: str = ""
