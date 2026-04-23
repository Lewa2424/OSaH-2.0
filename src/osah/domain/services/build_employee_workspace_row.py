from collections.abc import Iterable

from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_module_status_summary import EmployeeModuleStatusSummary
from osah.domain.entities.employee_problem import EmployeeProblem
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.format_employee_status_label import format_employee_status_label
from osah.domain.services.rank_employee_status_level import rank_employee_status_level


# ###### ПОБУДОВА РЯДКА ПРАЦІВНИКА / BUILD EMPLOYEE ROW ######
def build_employee_workspace_row(
    employee: Employee,
    training_records: Iterable[TrainingRecord],
    ppe_records: Iterable[PpeRecord],
    medical_records: Iterable[MedicalRecord],
    work_permit_records: Iterable[WorkPermitRecord],
) -> EmployeeWorkspaceRow:
    """Збирає один рядок робочого простору працівників без UI-логіки.
    Builds one employee workspace row without UI logic.
    """

    training_records_tuple = tuple(training_records)
    training_summary, training_problems = _build_training_summary(training_records_tuple)
    ppe_records_tuple = tuple(ppe_records)
    ppe_summary, ppe_problems = _build_ppe_summary(ppe_records_tuple)
    medical_records_tuple = tuple(medical_records)
    medical_summary, medical_problems = _build_medical_summary(medical_records_tuple)
    work_permit_records_tuple = tuple(work_permit_records)
    permit_summary, permit_problems = _build_work_permit_summary(work_permit_records_tuple)

    module_summaries = (training_summary, ppe_summary, medical_summary, permit_summary)
    problems = training_problems + ppe_problems + medical_problems + permit_problems

    if employee.employment_status.lower() in {"archived", "inactive", "dismissed"}:
        status_level = EmployeeStatusLevel.ARCHIVED
        status_reason = "працівник неактивний або в архіві"
    elif problems:
        top_problem = max(problems, key=lambda item: rank_employee_status_level(item.level))
        status_level = top_problem.level
        status_reason = top_problem.title
    else:
        status_level = EmployeeStatusLevel.NORMAL
        status_reason = "блокуючих або попереджувальних сигналів немає"

    return EmployeeWorkspaceRow(
        employee=employee,
        status_level=status_level,
        status_label=format_employee_status_label(status_level),
        status_reason=status_reason,
        department_name=employee.department_name,
        site_name=_infer_site_name(employee.department_name),
        position_name=employee.position_name,
        photo_path=None,
        training_records=training_records_tuple,
        ppe_records=ppe_records_tuple,
        medical_records=medical_records_tuple,
        work_permit_records=work_permit_records_tuple,
        module_summaries=module_summaries,
        problems=problems,
    )


def _build_training_summary(
    records: tuple[TrainingRecord, ...],
) -> tuple[EmployeeModuleStatusSummary, tuple[EmployeeProblem, ...]]:
    """Будує підсумок інструктажів і список проблем працівника.
    Builds training summary and employee problem list.
    """

    if not records:
        problem = EmployeeProblem(
            module_name="Інструктажі",
            level=EmployeeStatusLevel.CRITICAL,
            title="відсутній обов'язковий інструктаж",
            detail="У працівника немає жодного запису інструктажу.",
            target_key="trainings",
        )
        return _module_summary("Інструктажі", problem.level, "Критично", problem.title), (problem,)

    if any(record.status == TrainingStatus.OVERDUE for record in records):
        problem = EmployeeProblem(
            module_name="Інструктажі",
            level=EmployeeStatusLevel.CRITICAL,
            title="інструктаж прострочено",
            detail="Є інструктаж із простроченою датою наступного контролю.",
            target_key="trainings",
        )
        return _module_summary("Інструктажі", problem.level, "Критично", problem.title), (problem,)

    if any(record.status == TrainingStatus.WARNING for record in records):
        problem = EmployeeProblem(
            module_name="Інструктажі",
            level=EmployeeStatusLevel.WARNING,
            title="наближається строк інструктажу",
            detail="Один або кілька інструктажів скоро потребують повторного контролю.",
            target_key="trainings",
        )
        return _module_summary("Інструктажі", problem.level, "Увага", problem.title), (problem,)

    return _module_summary("Інструктажі", EmployeeStatusLevel.NORMAL, "Норма", "актуально"), ()


def _build_ppe_summary(records: tuple[PpeRecord, ...]) -> tuple[EmployeeModuleStatusSummary, tuple[EmployeeProblem, ...]]:
    """Будує підсумок ЗІЗ і список проблем працівника.
    Builds PPE summary and employee problem list.
    """

    if not records:
        problem = EmployeeProblem(
            module_name="ЗІЗ",
            level=EmployeeStatusLevel.WARNING,
            title="немає записів ЗІЗ",
            detail="Для працівника не знайдено записів видачі або норми ЗІЗ.",
            target_key="ppe",
        )
        return _module_summary("ЗІЗ", problem.level, "Увага", problem.title), (problem,)

    critical_statuses = {PpeStatus.EXPIRED, PpeStatus.NOT_ISSUED}
    if any(record.status in critical_statuses for record in records):
        problem = EmployeeProblem(
            module_name="ЗІЗ",
            level=EmployeeStatusLevel.CRITICAL,
            title="обов'язковий ЗІЗ прострочений або не виданий",
            detail="Є запис ЗІЗ зі строком заміни, що минув, або обов'язковий ЗІЗ не видано.",
            target_key="ppe",
        )
        return _module_summary("ЗІЗ", problem.level, "Критично", problem.title), (problem,)

    if any(record.status == PpeStatus.WARNING for record in records):
        problem = EmployeeProblem(
            module_name="ЗІЗ",
            level=EmployeeStatusLevel.WARNING,
            title="наближається строк заміни ЗІЗ",
            detail="Один або кілька записів ЗІЗ наближаються до строку заміни.",
            target_key="ppe",
        )
        return _module_summary("ЗІЗ", problem.level, "Увага", problem.title), (problem,)

    return _module_summary("ЗІЗ", EmployeeStatusLevel.NORMAL, "Норма", "забезпечення актуальне"), ()


def _build_medical_summary(
    records: tuple[MedicalRecord, ...],
) -> tuple[EmployeeModuleStatusSummary, tuple[EmployeeProblem, ...]]:
    """Будує підсумок меддопуску і список проблем працівника.
    Builds medical admission summary and employee problem list.
    """

    if not records:
        problem = EmployeeProblem(
            module_name="Медицина",
            level=EmployeeStatusLevel.CRITICAL,
            title="меддопуск відсутній",
            detail="У працівника немає чинного запису медичного допуску.",
            target_key="medical",
        )
        return _module_summary("Медицина", problem.level, "Критично", problem.title), (problem,)

    if any(record.status in {MedicalStatus.EXPIRED, MedicalStatus.NOT_FIT} for record in records):
        problem = EmployeeProblem(
            module_name="Медицина",
            level=EmployeeStatusLevel.CRITICAL,
            title="меддопуск прострочено або робота заборонена",
            detail="Є медичний запис зі строком, що минув, або рішенням 'не придатний'.",
            target_key="medical",
        )
        return _module_summary("Медицина", problem.level, "Критично", problem.title), (problem,)

    if any(record.status == MedicalStatus.RESTRICTED for record in records):
        problem = EmployeeProblem(
            module_name="Медицина",
            level=EmployeeStatusLevel.RESTRICTED,
            title="є обмеження за меддопуском",
            detail="Працівник допущений не до всіх видів робіт.",
            target_key="medical",
        )
        return _module_summary("Медицина", problem.level, "Обмежено", problem.title), (problem,)

    if any(record.status == MedicalStatus.WARNING for record in records):
        problem = EmployeeProblem(
            module_name="Медицина",
            level=EmployeeStatusLevel.WARNING,
            title="наближається строк меддопуску",
            detail="Медичний допуск скоро потребує повторного контролю.",
            target_key="medical",
        )
        return _module_summary("Медицина", problem.level, "Увага", problem.title), (problem,)

    return _module_summary("Медицина", EmployeeStatusLevel.NORMAL, "Норма", "допуск чинний"), ()


def _build_work_permit_summary(
    records: tuple[WorkPermitRecord, ...],
) -> tuple[EmployeeModuleStatusSummary, tuple[EmployeeProblem, ...]]:
    """Будує підсумок нарядів-допусків і список проблем працівника.
    Builds work permit summary and employee problem list.
    """

    active_records = tuple(record for record in records if record.status not in {WorkPermitStatus.CLOSED, WorkPermitStatus.CANCELED})
    if any(record.status in {WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID} for record in active_records):
        problem = EmployeeProblem(
            module_name="Наряди-допуски",
            level=EmployeeStatusLevel.CRITICAL,
            title="наряд-допуск прострочено і не закрито",
            detail="Працівник є учасником наряду-допуску, строк якого минув без закриття.",
            target_key="work_permits",
        )
        return _module_summary("Наряди-допуски", problem.level, "Критично", problem.title), (problem,)

    if any(record.status == WorkPermitStatus.WARNING for record in active_records):
        problem = EmployeeProblem(
            module_name="Наряди-допуски",
            level=EmployeeStatusLevel.WARNING,
            title="наряд-допуск скоро завершується",
            detail="Є активний наряд-допуск із близьким строком завершення.",
            target_key="work_permits",
        )
        return _module_summary("Наряди-допуски", problem.level, "Увага", problem.title), (problem,)

    if active_records:
        return _module_summary("Наряди-допуски", EmployeeStatusLevel.NORMAL, "Активно", "чинні наряди без критики"), ()

    return _module_summary("Наряди-допуски", EmployeeStatusLevel.NORMAL, "Норма", "активних проблем немає"), ()


def _module_summary(
    module_name: str,
    level: EmployeeStatusLevel,
    label: str,
    reason: str,
) -> EmployeeModuleStatusSummary:
    """Створює короткий модульний підсумок для картки працівника.
    Creates a compact module summary for an employee card.
    """

    return EmployeeModuleStatusSummary(module_name=module_name, level=level, label=label, reason=reason)


def _infer_site_name(department_name: str) -> str:
    """Виводить робочий участок із назви підрозділу для першої версії.
    Infers a work site from department name for the first version.
    """

    lowered = department_name.lower()
    if "дільниц" in lowered:
        return department_name
    if "служба" in lowered or "адміністрац" in lowered:
        return "Адміністративний контур"
    return "Основний виробничий контур"
