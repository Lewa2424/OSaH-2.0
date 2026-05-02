from datetime import datetime, timedelta

from osah.domain.entities.employee_topbar_summary import EmployeeTopbarSummary
from osah.domain.entities.employee_workspace import EmployeeWorkspace


# ###### КАДРОВА СВОДКА ДЛЯ ВЕРХНЬОЇ ПАНЕЛІ / EMPLOYEE TOPBAR SUMMARY ######
def build_employee_topbar_summary(workspace: EmployeeWorkspace, now: datetime | None = None) -> EmployeeTopbarSummary:
    """Будує коротку кадрову сводку для topbar.
    Builds compact employee summary for the top command bar.
    """

    reference_now = now or datetime.now()
    new_threshold = reference_now - timedelta(days=14)
    active_rows = tuple(
        row
        for row in workspace.rows
        if row.employee.employment_status.strip().lower() == "active"
    )
    archived_rows = tuple(
        row
        for row in workspace.rows
        if row.employee.employment_status.strip().lower() in {"archived", "inactive", "dismissed"}
    )
    return EmployeeTopbarSummary(
        active_employee_count=len(active_rows),
        department_count=len({row.department_name for row in workspace.rows if row.department_name}),
        new_employee_count=sum(
            1
            for row in active_rows
            if _is_created_after(row.employee.created_at_text, new_threshold)
        ),
        archived_employee_count=len(archived_rows),
    )


# ###### ПЕРЕВІРКА ДАТИ СТВОРЕННЯ / CREATED DATE CHECK ######
def _is_created_after(created_at_text: str, threshold: datetime) -> bool:
    """Перевіряє, чи створена картка після заданого порогу.
    Checks whether the card was created after the given threshold.
    """

    if not created_at_text:
        return False
    try:
        normalized_text = created_at_text.replace("Z", "").replace("T", " ")
        return datetime.fromisoformat(normalized_text) >= threshold
    except ValueError:
        return False
