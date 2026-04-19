from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.services.assess_employee_registry_notifications import assess_employee_registry_notifications


# ###### ПОБУДОВА СПОВІЩЕНЬ РЕЄСТРУ / ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ РЕЕСТРА ######
def build_registry_notifications(employees: tuple[Employee, ...]) -> tuple[NotificationItem, ...]:
    """Збирає всі активні сповіщення на основі поточного реєстру працівників.
    Собирает все активные уведомления на основе текущего реестра сотрудников.
    """

    notifications: list[NotificationItem] = []
    for employee in employees:
        notifications.extend(assess_employee_registry_notifications(employee))
    return tuple(notifications)
