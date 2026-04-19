from osah.domain.entities.employee import Employee
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_registry_row import TrainingRegistryRow
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ПОБУДОВА РЯДКІВ РЕЄСТРУ ІНСТРУКТАЖІВ / ПОСТРОЕНИЕ СТРОК РЕЕСТРА ИНСТРУКТАЖЕЙ ######
def build_training_registry_rows(
    employees: tuple[Employee, ...],
    training_records: tuple[TrainingRecord, ...],
) -> tuple[TrainingRegistryRow, ...]:
    """Повертає повний набір рядків реєстру, включно зі станом відсутності записів.
    Возвращает полный набор строк реестра, включая состояние отсутствия записей.
    """

    rows: list[TrainingRegistryRow] = []
    records_by_employee: dict[str, list[TrainingRecord]] = {}
    for training_record in training_records:
        records_by_employee.setdefault(training_record.employee_personnel_number, []).append(training_record)

    for employee in employees:
        if employee.employment_status.strip().lower() != "active":
            continue

        employee_records = records_by_employee.get(employee.personnel_number, [])
        if not employee_records:
            rows.append(
                TrainingRegistryRow(
                    employee_personnel_number=employee.personnel_number,
                    employee_full_name=employee.full_name,
                    training_type_label="Немає записів",
                    event_date_label="-",
                    next_control_date_label="-",
                    status_label="Відсутній",
                    conducted_by_label="-",
                    row_filter=TrainingRegistryFilter.MISSING,
                )
            )
            continue

        for training_record in sorted(employee_records, key=lambda current_record: current_record.next_control_date):
            rows.append(
                TrainingRegistryRow(
                    employee_personnel_number=training_record.employee_personnel_number,
                    employee_full_name=training_record.employee_full_name,
                    training_type_label=format_training_type_label(training_record.training_type),
                    event_date_label=training_record.event_date,
                    next_control_date_label=training_record.next_control_date,
                    status_label=_format_training_status(training_record.status),
                    conducted_by_label=training_record.conducted_by,
                    row_filter=_map_status_to_filter(training_record.status),
                )
            )

    return tuple(rows)


# ###### ФОРМАТУВАННЯ СТАТУСУ РЯДКА / ФОРМАТИРОВАНИЕ СТАТУСА СТРОКИ ######
def _format_training_status(training_status: TrainingStatus) -> str:
    """Повертає локалізовану мітку статусу для рядка реєстру.
    Возвращает локализованную метку статуса для строки реестра.
    """

    if training_status == TrainingStatus.CURRENT:
        return "Актуально"
    if training_status == TrainingStatus.WARNING:
        return "Увага"
    return "Прострочено"


# ###### ВІДПОВІДНІСТЬ СТАТУСУ ФІЛЬТРУ / СООТВЕТСТВИЕ СТАТУСА ФИЛЬТРУ ######
def _map_status_to_filter(training_status: TrainingStatus) -> TrainingRegistryFilter:
    """Повертає фільтр, якому відповідає статус інструктажу.
    Возвращает фильтр, которому соответствует статус инструктажа.
    """

    if training_status == TrainingStatus.CURRENT:
        return TrainingRegistryFilter.CURRENT
    if training_status == TrainingStatus.WARNING:
        return TrainingRegistryFilter.WARNING
    return TrainingRegistryFilter.OVERDUE
