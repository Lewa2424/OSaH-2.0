import unittest

from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.build_work_permit_notifications import build_work_permit_notifications


class BuildWorkPermitNotificationsTests(unittest.TestCase):
    """Тести контрольних сповіщень по нарядах.
    Tests for work permit control notifications.
    """

    def test_build_work_permit_notifications_creates_generic_alert_without_participants(self) -> None:
        """Проблемний легкий запис все одно дає сповіщення.
        An invalid lightweight entry still produces a notification.
        """

        notifications = build_work_permit_notifications(
            employees=(
                Employee(
                    personnel_number="0001",
                    full_name="Працівник",
                    position_name="Монтажник",
                    department_name="Цех",
                    employment_status="active",
                ),
            ),
            work_permit_records=(
                WorkPermitRecord(
                    record_id=1,
                    permit_number="НД-777",
                    work_kind="Ремонтні роботи",
                    work_location="Цех 7",
                    starts_at="2026-04-10 08:00",
                    ends_at="2026-04-10 12:00",
                    responsible_person="",
                    issuer_person="",
                    note_text="",
                    closed_at=None,
                    participants=(),
                    status=WorkPermitStatus.INVALID,
                    target_training_status=WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED,
                ),
            ),
        )

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].notification_level, NotificationLevel.CRITICAL)
        self.assertIsNone(notifications[0].employee_personnel_number)


if __name__ == "__main__":
    unittest.main()
