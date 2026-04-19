import unittest

from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.assess_employee_registry_notifications import assess_employee_registry_notifications


class AssessEmployeeRegistryNotificationsTests(unittest.TestCase):
    """Тести оцінки сповіщень реєстру працівників.
    Тесты оценки уведомлений реестра сотрудников.
    """

    # ###### ПЕРЕВІРКА ПОПЕРЕДЖЕНЬ НЕПОВНОЇ КАРТКИ / ПРОВЕРКА ПРЕДУПРЕЖДЕНИЙ НЕПОЛНОЙ КАРТОЧКИ ######
    def test_assess_employee_registry_notifications_returns_warning_for_missing_department(self) -> None:
        """Перевіряє формування попередження при відсутньому підрозділі.
        Проверяет формирование предупреждения при отсутствующем подразделении.
        """

        employee = Employee(
            personnel_number="1001",
            full_name="Тестовий Працівник",
            position_name="Слюсар",
            department_name="",
            employment_status="active",
        )

        notifications = assess_employee_registry_notifications(employee)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].notification_level, NotificationLevel.WARNING)
        self.assertEqual(notifications[0].title_text, "Не заповнений підрозділ")

    # ###### ПЕРЕВІРКА КРИТИЧНОГО СИГНАЛУ БЕЗ ПІБ / ПРОВЕРКА КРИТИЧЕСКОГО СИГНАЛА БЕЗ ФИО ######
    def test_assess_employee_registry_notifications_returns_critical_for_missing_full_name(self) -> None:
        """Перевіряє формування критичного сигналу при відсутньому ПІБ.
        Проверяет формирование критического сигнала при отсутствующем ФИО.
        """

        employee = Employee(
            personnel_number="1002",
            full_name="",
            position_name="Слюсар",
            department_name="Цех 1",
            employment_status="active",
        )

        notifications = assess_employee_registry_notifications(employee)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].notification_level, NotificationLevel.CRITICAL)
        self.assertEqual(notifications[0].title_text, "Відсутнє ПІБ працівника")


if __name__ == "__main__":
    unittest.main()
