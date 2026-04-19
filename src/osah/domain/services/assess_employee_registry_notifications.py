from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel


# ###### ОЦІНКА СПОВІЩЕНЬ РЕЄСТРУ ПРАЦІВНИКА / ОЦЕНКА УВЕДОМЛЕНИЙ РЕЕСТРА СОТРУДНИКА ######
def assess_employee_registry_notifications(employee: Employee) -> tuple[NotificationItem, ...]:
    """Повертає системні сповіщення за цілісністю картки працівника.
    Возвращает системные уведомления по целостности карточки сотрудника.
    """

    notifications: list[NotificationItem] = []
    personnel_number = employee.personnel_number.strip()
    full_name = employee.full_name.strip()
    position_name = employee.position_name.strip()
    department_name = employee.department_name.strip()
    employment_status = employee.employment_status.strip().lower()

    if not personnel_number:
        notifications.append(
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.CRITICAL,
                source_module="employees.registry",
                title_text="Відсутній табельний номер",
                message_text="Картка працівника не має табельного номера, тому її не можна безпечно використовувати в імпорті та контролі.",
                employee_full_name=full_name or None,
            )
        )

    if not full_name:
        notifications.append(
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.CRITICAL,
                source_module="employees.registry",
                title_text="Відсутнє ПІБ працівника",
                message_text="Картка працівника не має ПІБ, тому її потрібно виправити до подальшої роботи.",
                employee_personnel_number=personnel_number or None,
            )
        )

    if not position_name:
        notifications.append(
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.WARNING,
                source_module="employees.registry",
                title_text="Не заповнена посада",
                message_text="У картці працівника відсутня посада. Це послаблює подальший контроль за правилами ОП.",
                employee_personnel_number=personnel_number or None,
                employee_full_name=full_name or None,
            )
        )

    if not department_name:
        notifications.append(
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.WARNING,
                source_module="employees.registry",
                title_text="Не заповнений підрозділ",
                message_text="У картці працівника відсутній підрозділ. Це ускладнює дерево структури та звітність.",
                employee_personnel_number=personnel_number or None,
                employee_full_name=full_name or None,
            )
        )

    if employment_status and employment_status not in {"active", "archived"}:
        notifications.append(
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.INFO,
                source_module="employees.registry",
                title_text="Нестандартний статус зайнятості",
                message_text=f"Картка працівника має нестандартний статус зайнятості: '{employee.employment_status}'.",
                employee_personnel_number=personnel_number or None,
                employee_full_name=full_name or None,
            )
        )

    return tuple(notifications)
