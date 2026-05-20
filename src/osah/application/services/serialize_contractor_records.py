import json

from osah.domain.entities.contractor_record import ContractorRecord


def serialize_contractor_records(records: tuple[ContractorRecord, ...]) -> str:
    """?????????? ?????? ??????????? ??? staged-??????????.
    Serializes contractors registry for staged persistence.
    """

    return json.dumps(
        [
            {
                "contractor_id": record.contractor_id,
                "company_name": record.company_name,
                "contact_person": record.contact_person,
                "contact_phone": record.contact_phone,
                "contact_email": record.contact_email,
                "activity_status": record.activity_status,
                "note_text": record.note_text,
                "enterprise_supervisor": record.enterprise_supervisor,
                "work_scope_text": record.work_scope_text,
                "workers": [
                    {
                        "worker_id": worker.worker_id,
                        "full_name": worker.full_name,
                        "role_name": worker.role_name,
                        "training_ok": worker.training_ok,
                        "ppe_ok": worker.ppe_ok,
                        "medical_ok": worker.medical_ok,
                        "access_ok": worker.access_ok,
                        "note_text": worker.note_text,
                    }
                    for worker in record.workers
                ],
            }
            for record in sorted(records, key=lambda value: (value.company_name.lower(), value.contractor_id))
        ],
        ensure_ascii=False,
    )
