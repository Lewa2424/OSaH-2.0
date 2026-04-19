from osah.application.services.application_context import ApplicationContext
from osah.application.services.ensure_startup_auto_backup import ensure_startup_auto_backup
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.security.ensure_security_baseline import ensure_security_baseline
from osah.application.services.send_daily_report_if_due import send_daily_report_if_due
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.infrastructure.config.application_paths import ApplicationPaths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema
from osah.infrastructure.database.seed.seed_demo_employees import seed_demo_employees
from osah.infrastructure.logging.configure_logging import configure_logging
from osah.infrastructure.logging.log_system_event import log_system_event


# ###### ІНІЦІАЛІЗАЦІЯ ЗАСТОСУНКУ / ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ######
def initialize_application(application_paths: ApplicationPaths) -> ApplicationContext:
    """Готує каталоги, логування, базу даних і базовий security-профіль.
    Подготавливает каталоги, логирование, базу данных и базовый security-профиль.
    """

    application_paths.data_directory.mkdir(parents=True, exist_ok=True)
    application_paths.log_directory.mkdir(parents=True, exist_ok=True)
    configure_logging(application_paths.log_file_path)
    log_system_event("bootstrap", "Application bootstrap started.")

    connection = create_database_connection(application_paths.database_file_path)
    try:
        ensure_core_schema(connection)
        seed_demo_employees(connection)
        sync_control_notifications(connection)
    finally:
        connection.close()

    ensure_security_baseline(application_paths.database_file_path)
    ensure_startup_auto_backup(application_paths.database_file_path)
    send_daily_report_if_due(application_paths.database_file_path)
    log_system_event("bootstrap", "Application bootstrap completed successfully.")

    return ApplicationContext(
        database_path=application_paths.database_file_path,
        log_path=application_paths.log_file_path,
        dashboard_snapshot=load_dashboard_snapshot_from_path(application_paths.database_file_path),
    )
