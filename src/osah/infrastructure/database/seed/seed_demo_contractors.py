import json
from sqlite3 import Connection

from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_worker import ContractorWorker
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.infrastructure.database.seed.build_demo_contractor_records import build_demo_contractor_records

_CONTRACTOR_REGISTRY_SETTING_KEY = "contractors.registry_v1"


def seed_demo_contractors(connection: Connection) -> None:
    """Додає демо-підрядників до staged-реєстру без дублювання.
    Adds demo contractors into staged registry without duplicates.
    """

    app_settings = list_app_settings(connection)
    existing_records = _deserialize_records(app_settings.get(_CONTRACTOR_REGISTRY_SETTING_KEY, "[]"))
    records_by_id = {record.contractor_id: record for record in existing_records}
    for record in build_demo_contractor_records():
        records_by_id.setdefault(record.contractor_id, record)
    upsert_app_setting(connection, _CONTRACTOR_REGISTRY_SETTING_KEY, _serialize_records(tuple(records_by_id.values())))


def _deserialize_records(raw_value: str) -> tuple[ContractorRecord, ...]:
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        payload = []
    if not isinstance(payload, list):
        return ()
    records: list[ContractorRecord] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        company_name = str(item.get("company_name", "")).strip()
        contractor_id = str(item.get("contractor_id", "")).strip()
        if not company_name or not contractor_id:
            continue
        records.append(
            ContractorRecord(
                contractor_id=contractor_id,
                company_name=company_name,
                contact_person=str(item.get("contact_person", "")).strip(),
                contact_phone=str(item.get("contact_phone", "")).strip(),
                contact_email=str(item.get("contact_email", "")).strip(),
                activity_status=str(item.get("activity_status", "active")).strip() or "active",
                note_text=str(item.get("note_text", "")).strip(),
                enterprise_supervisor=str(item.get("enterprise_supervisor", "")).strip(),
                work_scope_text=str(item.get("work_scope_text", "")).strip(),
                workers=_deserialize_workers(item.get("workers", [])),
            )
        )
    return tuple(records)


def _deserialize_workers(raw_workers: object) -> tuple[ContractorWorker, ...]:
    if not isinstance(raw_workers, list):
        return ()
    workers: list[ContractorWorker] = []
    for item in raw_workers:
        if not isinstance(item, dict):
            continue
        full_name = str(item.get("full_name", "")).strip()
        if not full_name:
            continue
        workers.append(
            ContractorWorker(
                worker_id=str(item.get("worker_id", "")).strip() or full_name.lower().replace(" ", "-"),
                full_name=full_name,
                role_name=str(item.get("role_name", "")).strip(),
                training_ok=bool(item.get("training_ok", False)),
                ppe_ok=bool(item.get("ppe_ok", False)),
                medical_ok=bool(item.get("medical_ok", False)),
                access_ok=bool(item.get("access_ok", False)),
                note_text=str(item.get("note_text", "")).strip(),
            )
        )
    return tuple(workers)


def _serialize_records(records: tuple[ContractorRecord, ...]) -> str:
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
