from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_item import NotificationItem


# ###### ПРИВ'ЯЗКА СПОВІЩЕННЯ ДО РОЗДІЛУ / ПРИВЯЗКА УВЕДОМЛЕНИЯ К РАЗДЕЛУ ######
def map_notification_to_app_section(notification: NotificationItem) -> AppSection:
    """Повертає розділ shell, до якого належить системне сповіщення.
    Возвращает раздел shell, к которому относится системное уведомление.
    """

    if notification.source_module.startswith("employees."):
        return AppSection.EMPLOYEES
    if notification.source_module.startswith("trainings."):
        return AppSection.TRAININGS
    if notification.source_module.startswith("ppe."):
        return AppSection.PPE
    if notification.source_module.startswith("medical."):
        return AppSection.MEDICAL
    if notification.source_module.startswith("work_permits."):
        return AppSection.WORK_PERMITS
    return AppSection.DASHBOARD
