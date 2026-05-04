from dataclasses import dataclass

from osah.domain.entities.employee_readiness_level import EmployeeReadinessLevel


@dataclass(slots=True)
class EmployeeWorkReadiness:
    """Стан готовності працівника за інструктажами, медициною та ЗІЗ.
    Employee readiness snapshot across trainings, medicals, and PPE.
    """

    employee_personnel_number: str
    training_level: EmployeeReadinessLevel
    training_message: str
    medical_level: EmployeeReadinessLevel
    medical_message: str
    ppe_level: EmployeeReadinessLevel
    ppe_message: str
