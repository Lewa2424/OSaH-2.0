from sqlite3 import Connection

from osah.domain.services.build_medical_notifications import build_medical_notifications
from osah.domain.services.build_ppe_notifications import build_ppe_notifications
from osah.domain.services.build_registry_notifications import build_registry_notifications
from osah.domain.services.build_training_notifications import build_training_notifications
from osah.domain.services.build_work_permit_notifications import build_work_permit_notifications
from osah.infrastructure.database.commands.replace_notifications import replace_notifications
from osah.infrastructure.database.queries.list_employees import list_employees
from osah.infrastructure.database.queries.list_medical_records import list_medical_records
from osah.infrastructure.database.queries.list_ppe_records import list_ppe_records
from osah.infrastructure.database.queries.list_training_records import list_training_records
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


# ###### СИНХРОНІЗАЦІЯ КОНТРОЛЬНИХ СПОВІЩЕНЬ / СИНХРОНИЗАЦИЯ КОНТРОЛЬНЫХ УВЕДОМЛЕНИЙ ######
def sync_control_notifications(connection: Connection) -> None:
    """Перераховує і зберігає активні контрольні сповіщення системи.
    Пересчитывает и сохраняет активные контрольные уведомления системы.
    """

    employees = list_employees(connection)
    training_records = list_training_records(connection)
    ppe_records = list_ppe_records(connection)
    medical_records = list_medical_records(connection)
    work_permit_records = list_work_permit_records(connection)
    notifications = (
        build_registry_notifications(employees)
        + build_training_notifications(employees, training_records)
        + build_ppe_notifications(employees, ppe_records)
        + build_medical_notifications(employees, medical_records)
        + build_work_permit_notifications(employees, work_permit_records)
    )
    replace_notifications(connection, notifications)
