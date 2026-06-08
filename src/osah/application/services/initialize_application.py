from osah.application.services.application_context import ApplicationContext
from osah.application.services.ensure_startup_auto_backup import ensure_startup_auto_backup
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.security.ensure_demo_distribution_timer import ensure_demo_distribution_timer
from osah.application.services.security.ensure_security_baseline import ensure_security_baseline
from osah.infrastructure.config.is_demo_timed_distribution_enabled import is_demo_timed_distribution_marker_present
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.infrastructure.config.application_paths import ApplicationPaths
from osah.infrastructure.config.is_demo_seed_enabled import is_demo_seed_enabled
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema
from osah.infrastructure.database.seed.seed_demo_contractors import seed_demo_contractors
from osah.infrastructure.database.seed.seed_demo_employees import seed_demo_employees
from osah.infrastructure.database.seed.seed_port_risk_registry import seed_port_risk_registry
from osah.infrastructure.database.seed.seed_port_risk_registry_tags import seed_port_risk_registry_tags
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
        seed_port_risk_registry(
            connection,
            application_paths.project_root / "for_data" / "Ризики в порту.xlsx",
        )
        seed_port_risk_registry_tags(connection)
        if is_demo_seed_enabled():
            seed_demo_employees(connection)
            seed_demo_contractors(connection)
        ensure_demo_distribution_timer(connection, application_paths.project_root)
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()

    ensure_security_baseline(application_paths.database_file_path)
    ensure_startup_auto_backup(application_paths.database_file_path)
    if is_demo_seed_enabled():
        log_system_event("bootstrap", "Demo seed enabled for this run.")
    else:
        log_system_event("bootstrap", "Demo seed disabled; production bootstrap uses a clean database.")
    if is_demo_timed_distribution_marker_present(application_paths.project_root):
        log_system_event("bootstrap", "Demo-only timed distribution marker detected.")
    log_system_event("bootstrap", "Application bootstrap completed successfully.")

    return ApplicationContext(
        database_path=application_paths.database_file_path,
        log_path=application_paths.log_file_path,
        dashboard_snapshot=load_dashboard_snapshot_from_path(application_paths.database_file_path),
    )
