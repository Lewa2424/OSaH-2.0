from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow


# ###### БЛОК ПРАЦІВНИКА У ЗВІТІ / BUILD DAILY REPORT EMPLOYEE BLOCK ######
def build_daily_report_employee_block(row: EmployeeWorkspaceRow) -> str:
    """Повертає багаторядковий блок ідентифікації працівника для таблиці звіту.
    Returns a multiline employee identification block for the report table.
    """

    return (
        f"таб. № {row.employee.personnel_number}\n"
        f"{row.position_name}\n"
        f"{row.employee.full_name}"
    )
