from sqlite3 import Connection


# ###### СТВОРЕННЯ БАЗОВОЇ СХЕМИ / СОЗДАНИЕ БАЗОВОЙ СХЕМЫ ######
def ensure_core_schema(connection: Connection) -> None:
    """Створює мінімальну робочу схему для першого зрізу застосунку.
    Создаёт минимальную рабочую схему для первого среза приложения.
    """

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_number TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            position_name TEXT NOT NULL,
            department_name TEXT NOT NULL,
            employment_status TEXT NOT NULL,
            photo_path TEXT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            module_name TEXT NOT NULL,
            event_level TEXT NOT NULL,
            actor_name TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            result_status TEXT NOT NULL,
            description_text TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notification_kind TEXT NOT NULL,
            notification_level TEXT NOT NULL,
            source_module TEXT NOT NULL,
            title_text TEXT NOT NULL,
            message_text TEXT NOT NULL,
            employee_personnel_number TEXT NULL,
            employee_full_name TEXT NULL,
            state_name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_personnel_number TEXT NOT NULL,
            training_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            next_control_date TEXT NOT NULL,
            conducted_by TEXT NOT NULL,
            note_text TEXT NOT NULL DEFAULT '',
            work_risk_category TEXT NOT NULL DEFAULT 'not_applicable',
            next_control_basis TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_personnel_number)
                REFERENCES employees(personnel_number)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS ppe_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_personnel_number TEXT NOT NULL,
            ppe_name TEXT NOT NULL,
            is_required INTEGER NOT NULL,
            is_issued INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            replacement_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            note_text TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_personnel_number)
                REFERENCES employees(personnel_number)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_personnel_number TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            valid_until TEXT NOT NULL,
            medical_decision TEXT NOT NULL,
            restriction_note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_personnel_number)
                REFERENCES employees(personnel_number)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS work_permits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            permit_number TEXT NOT NULL UNIQUE,
            work_kind TEXT NOT NULL,
            work_location TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            ends_at TEXT NOT NULL,
            responsible_person TEXT NOT NULL,
            issuer_person TEXT NOT NULL,
            note_text TEXT NOT NULL DEFAULT '',
            closed_at TEXT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS work_permit_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_permit_id INTEGER NOT NULL,
            employee_personnel_number TEXT NOT NULL,
            participant_role TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (work_permit_id)
                REFERENCES work_permits(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (employee_personnel_number)
                REFERENCES employees(personnel_number)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS import_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            source_format TEXT NOT NULL,
            entity_scope TEXT NOT NULL,
            draft_total INTEGER NOT NULL DEFAULT 0,
            valid_total INTEGER NOT NULL DEFAULT 0,
            invalid_total INTEGER NOT NULL DEFAULT 0,
            applied_at TEXT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS employee_import_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            source_row_number INTEGER NOT NULL,
            personnel_number TEXT NOT NULL DEFAULT '',
            full_name TEXT NOT NULL DEFAULT '',
            position_name TEXT NOT NULL DEFAULT '',
            department_name TEXT NOT NULL DEFAULT '',
            employment_status TEXT NOT NULL DEFAULT '',
            resolution_status TEXT NOT NULL,
            issue_text TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id)
                REFERENCES import_batches(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS news_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            source_url TEXT NOT NULL UNIQUE,
            source_kind TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            is_trusted INTEGER NOT NULL DEFAULT 1,
            last_checked_at TEXT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS news_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            title_text TEXT NOT NULL,
            link_url TEXT NOT NULL,
            published_at_text TEXT NOT NULL DEFAULT '',
            source_kind TEXT NOT NULL,
            fingerprint_value TEXT NOT NULL,
            read_state TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id)
                REFERENCES news_sources(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            UNIQUE (source_id, fingerprint_value)
        );
        """
    )
    _ensure_work_permit_cancel_columns(connection)
    _ensure_training_control_columns(connection)
    connection.commit()


# ###### МІГРАЦІЯ ПОЛІВ СКАСУВАННЯ НАРЯДУ / WORK PERMIT CANCEL COLUMNS MIGRATION ######
def _ensure_work_permit_cancel_columns(connection: Connection) -> None:
    """Додає nullable-поля скасування наряду до вже існуючих локальних баз.
    Adds nullable work permit cancel fields to already existing local databases.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(work_permits);").fetchall()
    }
    if "canceled_at" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN canceled_at TEXT NULL;")
    if "cancel_reason_text" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN cancel_reason_text TEXT NOT NULL DEFAULT '';")
    _ensure_employee_photo_column(connection)


# ###### МІГРАЦІЯ ПОЛЯ ФОТО ПРАЦІВНИКА / EMPLOYEE PHOTO COLUMN MIGRATION ######
def _ensure_employee_photo_column(connection: Connection) -> None:
    """Додає nullable-поле photo_path у employees для локальних баз попередніх версій.
    Adds nullable photo_path column in employees for previous local databases.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(employees);").fetchall()
    }
    if "photo_path" not in columns:
        connection.execute("ALTER TABLE employees ADD COLUMN photo_path TEXT NULL;")


# ###### МИГРАЦИЯ ПОЛЕЙ РАСЧЁТА ИНСТРУКТАЖЕЙ / TRAINING CONTROL COLUMNS MIGRATION ######
def _ensure_training_control_columns(connection: Connection) -> None:
    """Добавляет поля основания расчёта инструктажей в уже существующие локальные базы.
    Adds training calculation basis fields to already existing local databases.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(trainings);").fetchall()
    }
    if "work_risk_category" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN work_risk_category TEXT NOT NULL DEFAULT 'not_applicable';"
        )
    if "next_control_basis" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN next_control_basis TEXT NOT NULL DEFAULT 'manual';"
        )
