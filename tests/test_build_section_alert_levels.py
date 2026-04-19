import unittest

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.build_section_alert_levels import build_section_alert_levels


class BuildSectionAlertLevelsTests(unittest.TestCase):
    """Тести побудови рівнів тривоги для розділів shell.
    Тесты построения уровней тревоги для разделов shell.
    """

    # ###### ПЕРЕВІРКА МАПІНГУ КРИТИЧНОСТІ РОЗДІЛІВ / ПРОВЕРКА МАППИНГА КРИТИЧНОСТИ РАЗДЕЛОВ ######
    def test_build_section_alert_levels_maps_notifications_to_sections(self) -> None:
        """Перевіряє, що сповіщення піднімають правильні рівні у відповідних розділах shell.
        Проверяет, что уведомления поднимают правильные уровни в соответствующих разделах shell.
        """

        notifications = (
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.WARNING,
                source_module="employees.registry",
                title_text="Не заповнений підрозділ",
                message_text="Потрібно заповнити підрозділ.",
            ),
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.CRITICAL,
                source_module="trainings.registry",
                title_text="Прострочений інструктаж",
                message_text="Інструктаж прострочений.",
            ),
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.WARNING,
                source_module="medical.registry",
                title_text="Наближається строк меддопуску",
                message_text="Потрібна увага.",
            ),
        )

        section_levels = build_section_alert_levels(notifications)

        self.assertEqual(section_levels[AppSection.EMPLOYEES], NotificationLevel.WARNING)
        self.assertEqual(section_levels[AppSection.TRAININGS], NotificationLevel.CRITICAL)
        self.assertEqual(section_levels[AppSection.MEDICAL], NotificationLevel.WARNING)
        self.assertEqual(section_levels[AppSection.DASHBOARD], NotificationLevel.CRITICAL)


if __name__ == "__main__":
    unittest.main()
