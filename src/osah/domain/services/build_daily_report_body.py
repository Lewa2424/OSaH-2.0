from datetime import datetime

from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.domain.services.build_notification_source_summary import build_notification_source_summary


# ###### ПОБУДОВА ТІЛА ЩОДЕННОГО ЗВІТУ / ПОСТРОЕНИЕ ТЕЛА ЕЖЕДНЕВНОГО ОТЧЁТА ######
def build_daily_report_body(created_at: datetime, dashboard_snapshot: DashboardSnapshot) -> str:
    """Повертає текст щоденного звіту для керівника.
    Возвращает текст ежедневного отчёта для руководителя.
    """

    source_summary_lines = build_notification_source_summary(dashboard_snapshot.active_notifications)
    source_summary_text = "\n".join(f"- {summary_line}" for summary_line in source_summary_lines) or "- Немає активних проблем"
    critical_notification_lines = "\n".join(
        f"- {notification.title_text}: {notification.message_text}"
        for notification in dashboard_snapshot.active_notifications[:8]
    ) or "- Активних сповіщень немає"

    return (
        f"Дата формування: {created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"Працівників у системі: {dashboard_snapshot.employee_total}\n"
        f"Критичних проблем: {dashboard_snapshot.critical_items}\n"
        f"Проблем, що потребують уваги: {dashboard_snapshot.warning_items}\n"
        f"Фокус дня: {dashboard_snapshot.focus_of_the_day}\n\n"
        "Розподіл проблем по контурах:\n"
        f"{source_summary_text}\n\n"
        "Перші активні сигнали:\n"
        f"{critical_notification_lines}\n"
    )
