from sqlite3 import Connection


# ###### СОЗДАНИЕ БАЗОВОЙ СХЕМЫ / ENSURE CORE SCHEMA ######
def ensure_core_schema(connection: Connection) -> None:
    """Создаёт минимальную рабочую схему для локальной базы.
    Creates the minimal working schema for the local database.
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
            person_category TEXT NOT NULL DEFAULT 'own_employee',
            requires_primary_on_workplace INTEGER NOT NULL DEFAULT 1,
            work_risk_category TEXT NOT NULL DEFAULT 'not_applicable',
            next_control_basis TEXT NOT NULL DEFAULT 'manual',
            knowledge_check_result TEXT NOT NULL DEFAULT 'legacy_not_tracked',
            work_admission_status TEXT NOT NULL DEFAULT 'legacy_not_tracked',
            knowledge_check_note TEXT NOT NULL DEFAULT '',
            basis_text TEXT NOT NULL DEFAULT '',
            basis_note TEXT NOT NULL DEFAULT '',
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
            provision_status TEXT NOT NULL DEFAULT 'legacy_not_tracked',
            compliance_check_state TEXT NOT NULL DEFAULT 'legacy_not_tracked',
            basis_text TEXT NOT NULL DEFAULT '',
            basis_note TEXT NOT NULL DEFAULT '',
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
            medical_exam_basis TEXT NOT NULL DEFAULT 'legacy_not_tracked',
            basis_text TEXT NOT NULL DEFAULT '',
            basis_note TEXT NOT NULL DEFAULT '',
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
            reissued_from_record_id INTEGER NULL,
            reissued_to_record_id INTEGER NULL,
            reissue_reason_text TEXT NOT NULL DEFAULT '',
            base_ends_at TEXT NOT NULL DEFAULT '',
            extension_count INTEGER NOT NULL DEFAULT 0,
            extended_at TEXT NULL,
            extension_reason_text TEXT NOT NULL DEFAULT '',
            responsible_person TEXT NOT NULL,
            issuer_person TEXT NOT NULL,
            note_text TEXT NOT NULL DEFAULT '',
            closed_at TEXT NULL,
            target_training_status TEXT NOT NULL DEFAULT 'legacy_not_tracked',
            target_training_date TEXT NOT NULL DEFAULT '',
            target_training_conducted_by TEXT NOT NULL DEFAULT '',
            target_training_note TEXT NOT NULL DEFAULT '',
            basis_text TEXT NOT NULL DEFAULT '',
            basis_note TEXT NOT NULL DEFAULT '',
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

        CREATE TABLE IF NOT EXISTS work_permit_daily_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_permit_id INTEGER NOT NULL,
            checked_at TEXT NOT NULL,
            checked_by TEXT NOT NULL,
            note_text TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (work_permit_id)
                REFERENCES work_permits(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS port_site_passports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passport_code TEXT NOT NULL UNIQUE,
            site_name TEXT NOT NULL,
            site_type TEXT NOT NULL DEFAULT '',
            site_location TEXT NOT NULL DEFAULT '',
            site_description TEXT NOT NULL DEFAULT '',
            work_kind TEXT NOT NULL DEFAULT '',
            typical_operations TEXT NOT NULL DEFAULT '',
            work_mode TEXT NOT NULL DEFAULT '',
            typical_cargo TEXT NOT NULL DEFAULT '',
            cargo_features TEXT NOT NULL DEFAULT '',
            main_equipment TEXT NOT NULL DEFAULT '',
            lifting_devices TEXT NOT NULL DEFAULT '',
            has_railway_zone INTEGER NOT NULL DEFAULT 0,
            has_auto_zone INTEGER NOT NULL DEFAULT 0,
            has_crane_zone INTEGER NOT NULL DEFAULT 0,
            crew_composition TEXT NOT NULL DEFAULT '',
            responsible_person TEXT NOT NULL DEFAULT '',
            has_contractors INTEGER NOT NULL DEFAULT 0,
            contractors_note TEXT NOT NULL DEFAULT '',
            zone_kind TEXT NOT NULL DEFAULT '',
            has_night_works INTEGER NOT NULL DEFAULT 0,
            weather_features TEXT NOT NULL DEFAULT '',
            has_limited_visibility INTEGER NOT NULL DEFAULT 0,
            has_height_work INTEGER NOT NULL DEFAULT 0,
            has_water_edge_work INTEGER NOT NULL DEFAULT 0,
            has_stack_edge_work INTEGER NOT NULL DEFAULT 0,
            communication_barrier TEXT NOT NULL DEFAULT '',
            has_communication_barrier INTEGER NOT NULL DEFAULT 0,
            fencing_barrier TEXT NOT NULL DEFAULT '',
            has_fencing_barrier INTEGER NOT NULL DEFAULT 0,
            has_signalman INTEGER NOT NULL DEFAULT 0,
            lighting_barrier TEXT NOT NULL DEFAULT '',
            has_lighting_barrier INTEGER NOT NULL DEFAULT 0,
            ppe_text TEXT NOT NULL DEFAULT '',
            additional_barriers TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'draft',
            calculated_profile TEXT NOT NULL DEFAULT 'not_calculated',
            final_profile TEXT NOT NULL DEFAULT 'not_calculated',
            profile_override_reason TEXT NOT NULL DEFAULT '',
            calculated_by TEXT NOT NULL DEFAULT '',
            calculated_at TEXT NULL,
            approved_by TEXT NOT NULL DEFAULT '',
            approved_at TEXT NULL,
            archived_at TEXT NULL,
            archive_reason TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS port_risk_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            risk_code TEXT NOT NULL UNIQUE,
            level_1 TEXT NOT NULL DEFAULT '',
            level_2 TEXT NOT NULL DEFAULT '',
            level_3 TEXT NOT NULL DEFAULT '',
            risk_situation TEXT NOT NULL,
            hazard_source TEXT NOT NULL DEFAULT '',
            occurrence_conditions TEXT NOT NULL DEFAULT '',
            consequences TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS port_site_risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passport_id INTEGER NOT NULL,
            registry_risk_id INTEGER NULL,
            risk_situation TEXT NOT NULL,
            hazard_source TEXT NOT NULL DEFAULT '',
            occurrence_conditions TEXT NOT NULL DEFAULT '',
            consequences TEXT NOT NULL DEFAULT '',
            assessment_reason TEXT NOT NULL DEFAULT '',
            risk_level TEXT NOT NULL DEFAULT '',
            method_note TEXT NOT NULL DEFAULT '',
            inspector_comment TEXT NOT NULL DEFAULT '',
            suggestion_reason TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'manual',
            addition_source TEXT NOT NULL DEFAULT 'manual',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (passport_id)
                REFERENCES port_site_passports(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (registry_risk_id)
                REFERENCES port_risk_registry(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS port_risk_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_code TEXT NOT NULL UNIQUE,
            label_uk TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS port_risk_registry_tags (
            registry_risk_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (registry_risk_id, tag_id),
            FOREIGN KEY (registry_risk_id)
                REFERENCES port_risk_registry(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (tag_id)
                REFERENCES port_risk_tags(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS port_passport_tags (
            passport_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (passport_id, tag_id),
            FOREIGN KEY (passport_id)
                REFERENCES port_site_passports(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (tag_id)
                REFERENCES port_risk_tags(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_port_site_passports_status
        ON port_site_passports(status);

        CREATE INDEX IF NOT EXISTS idx_port_site_passports_updated
        ON port_site_passports(updated_at);

        CREATE INDEX IF NOT EXISTS idx_port_site_risks_passport
        ON port_site_risks(passport_id);

        CREATE INDEX IF NOT EXISTS idx_port_site_risks_status
        ON port_site_risks(status);

        CREATE INDEX IF NOT EXISTS idx_port_risk_registry_levels
        ON port_risk_registry(level_1, level_2);

        CREATE TABLE IF NOT EXISTS port_macrovariable_thresholds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passport_id INTEGER NOT NULL,
            macrovariable TEXT NOT NULL,
            trigger_text TEXT NOT NULL DEFAULT '',
            k_value REAL NOT NULL DEFAULT 1.0,
            is_stop_trigger INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (passport_id)
                REFERENCES port_site_passports(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_port_macrovariable_thresholds_passport
        ON port_macrovariable_thresholds(passport_id);

        CREATE TABLE IF NOT EXISTS port_compensating_barriers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passport_id INTEGER NOT NULL,
            macrovariable TEXT NOT NULL DEFAULT 'B',
            barrier_name TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            k_comp REAL NOT NULL DEFAULT 0.9,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (passport_id)
                REFERENCES port_site_passports(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_port_compensating_barriers_passport
        ON port_compensating_barriers(passport_id);

        CREATE TABLE IF NOT EXISTS port_shift_checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passport_id INTEGER NOT NULL,
            shift_date TEXT NOT NULL DEFAULT '',
            shift_label TEXT NOT NULL DEFAULT '',
            responsible_person TEXT NOT NULL DEFAULT '',
            r_base REAL NOT NULL DEFAULT 1.0,
            r_dyn REAL NULL,
            zone TEXT NULL,
            decision TEXT NULL,
            active_barrier_id INTEGER NULL,
            stop_reason TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (passport_id)
                REFERENCES port_site_passports(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (active_barrier_id)
                REFERENCES port_compensating_barriers(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_port_shift_checklists_passport
        ON port_shift_checklists(passport_id);

        CREATE INDEX IF NOT EXISTS idx_port_shift_checklists_date
        ON port_shift_checklists(shift_date);

        CREATE TABLE IF NOT EXISTS port_shift_checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checklist_id INTEGER NOT NULL,
            macrovariable TEXT NOT NULL,
            threshold_id INTEGER NULL,
            is_triggered INTEGER NOT NULL DEFAULT 0,
            k_used REAL NOT NULL DEFAULT 1.0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (checklist_id)
                REFERENCES port_shift_checklists(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (threshold_id)
                REFERENCES port_macrovariable_thresholds(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_port_shift_checklist_items_checklist
        ON port_shift_checklist_items(checklist_id);

        CREATE TABLE IF NOT EXISTS port_shift_checklist_barriers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checklist_id INTEGER NOT NULL,
            barrier_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (checklist_id)
                REFERENCES port_shift_checklists(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (barrier_id)
                REFERENCES port_compensating_barriers(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_port_shift_checklist_barriers_unique
        ON port_shift_checklist_barriers(checklist_id, barrier_id);

        CREATE INDEX IF NOT EXISTS idx_port_shift_checklist_barriers_checklist
        ON port_shift_checklist_barriers(checklist_id);

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
    _ensure_training_normative_columns(connection)
    _ensure_training_source_columns(connection)
    _ensure_training_current_columns(connection)
    _ensure_ppe_normative_columns(connection)
    _ensure_medical_normative_columns(connection)
    _ensure_work_permit_target_training_columns(connection)
    _ensure_work_permit_extension_columns(connection)
    _ensure_work_permit_reissue_columns(connection)
    _ensure_app_settings_columns(connection)
    _ensure_port_passports_r_base_column(connection)
    _ensure_port_compensating_barriers_macrovariable_column(connection)
    _ensure_port_shift_checklist_barriers_table(connection)
    connection.commit()


# ###### МИГРАЦИЯ ПОЛЕЙ ОТМЕНЫ НАРЯДА / WORK PERMIT CANCEL COLUMNS MIGRATION ######
def _ensure_work_permit_cancel_columns(connection: Connection) -> None:
    """Добавляет nullable-поля отмены наряда в уже существующие базы.
    Adds nullable work-permit cancel fields to already existing databases.
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


# ###### МИГРАЦИЯ ПОЛЯ ФОТО СОТРУДНИКА / EMPLOYEE PHOTO COLUMN MIGRATION ######
def _ensure_employee_photo_column(connection: Connection) -> None:
    """Добавляет поле photo_path в employees для старых локальных баз.
    Adds the photo_path column in employees for older local databases.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(employees);").fetchall()
    }
    if "photo_path" not in columns:
        connection.execute("ALTER TABLE employees ADD COLUMN photo_path TEXT NULL;")


# ###### МИГРАЦИЯ ПОЛЕЙ КОНТЕКСТА ИНСТРУКТАЖА / TRAINING CONTEXT COLUMNS MIGRATION ######
def _ensure_training_control_columns(connection: Connection) -> None:
    """Добавляет поля контекста и расчёта инструктажей в уже существующие базы.
    Adds training context and calculation columns to already existing databases.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(trainings);").fetchall()
    }
    if "person_category" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN person_category TEXT NOT NULL DEFAULT 'own_employee';"
        )
    if "requires_primary_on_workplace" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN requires_primary_on_workplace INTEGER NOT NULL DEFAULT 1;"
        )
    if "work_risk_category" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN work_risk_category TEXT NOT NULL DEFAULT 'not_applicable';"
        )
    if "next_control_basis" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN next_control_basis TEXT NOT NULL DEFAULT 'manual';"
        )


def _ensure_training_normative_columns(connection: Connection) -> None:
    """Добавляет новые поля инструктажей без искажения старых записей.
    Adds training normative fields without distorting legacy records.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(trainings);").fetchall()
    }
    if "knowledge_check_result" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN knowledge_check_result TEXT NOT NULL DEFAULT 'legacy_not_tracked';"
        )
    if "work_admission_status" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN work_admission_status TEXT NOT NULL DEFAULT 'legacy_not_tracked';"
        )
    if "knowledge_check_note" not in columns:
        connection.execute(
            "ALTER TABLE trainings ADD COLUMN knowledge_check_note TEXT NOT NULL DEFAULT '';"
        )
    if "basis_text" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN basis_text TEXT NOT NULL DEFAULT '';")
    if "basis_note" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN basis_note TEXT NOT NULL DEFAULT '';")


def _ensure_training_current_columns(connection: Connection) -> None:
    """Додає поля актуальності інструктажів і безпечно позначає поточні записи.
    Adds training current/archive fields and safely marks current records.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(trainings);").fetchall()
    }
    added_columns = False
    if "is_current" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN is_current INTEGER NOT NULL DEFAULT 1;")
        added_columns = True
    if "archived_at" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN archived_at TEXT NULL;")
        added_columns = True
    if "archive_reason" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN archive_reason TEXT NOT NULL DEFAULT '';")
        added_columns = True
    if "replaced_by_record_id" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN replaced_by_record_id INTEGER NULL;")
        added_columns = True

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_trainings_current_employee_type
        ON trainings(employee_personnel_number, training_type, is_current);
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_trainings_employee_current
        ON trainings(employee_personnel_number, is_current);
        """
    )
    if added_columns:
        _backfill_training_current_state(connection)


def _backfill_training_current_state(connection: Connection) -> None:
    """Позначає актуальні та архівні training-записи у вже існуючих базах.
    Marks current and archived training records in already existing databases.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(trainings);").fetchall()
    }
    has_source_key = "source_key" in columns
    select_source_key = ", source_key" if has_source_key else ", '' AS source_key"
    rows = connection.execute(
        f"""
        SELECT id, employee_personnel_number, training_type, event_date{select_source_key}
        FROM trainings
        ORDER BY event_date ASC, id ASC;
        """
    ).fetchall()
    latest_regular_ids: dict[tuple[str, str], int] = {}
    latest_manual_targeted_ids: dict[str, int] = {}
    latest_targeted_source_ids: dict[str, int] = {}

    for row in rows:
        record_id = int(row["id"])
        employee_number = str(row["employee_personnel_number"])
        training_type = str(row["training_type"])
        source_key = str(row["source_key"] or "").strip()
        if training_type == "targeted":
            if source_key:
                latest_targeted_source_ids[source_key] = record_id
            else:
                latest_manual_targeted_ids[employee_number] = record_id
            continue
        latest_regular_ids[(employee_number, training_type)] = record_id

    current_ids = set(latest_regular_ids.values())
    current_ids.update(latest_manual_targeted_ids.values())
    current_ids.update(latest_targeted_source_ids.values())

    for row in rows:
        record_id = int(row["id"])
        if record_id in current_ids:
            connection.execute(
                """
                UPDATE trainings
                SET is_current = 1,
                    archived_at = NULL,
                    archive_reason = '',
                    replaced_by_record_id = NULL
                WHERE id = ?;
                """,
                (record_id,),
            )
            continue
        connection.execute(
            """
            UPDATE trainings
            SET is_current = 0,
                archived_at = COALESCE(archived_at, CURRENT_TIMESTAMP),
                archive_reason = CASE
                    WHEN archive_reason = '' THEN 'legacy_superseded'
                    ELSE archive_reason
                END
            WHERE id = ?;
            """,
            (record_id,),
        )


def _ensure_training_source_columns(connection: Connection) -> None:
    """Додає source-поля інструктажів для надійного зв'язку з модулем-джерелом.
    Adds training source fields for reliable linkage to the origin module.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(trainings);").fetchall()
    }
    if "source_module" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN source_module TEXT NOT NULL DEFAULT '';")
    if "source_record_id" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN source_record_id INTEGER NULL;")
    if "source_key" not in columns:
        connection.execute("ALTER TABLE trainings ADD COLUMN source_key TEXT NOT NULL DEFAULT '';")
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_trainings_source_key ON trainings(source_key);"
    )


def _ensure_ppe_normative_columns(connection: Connection) -> None:
    """Добавляет и безопасно инициализирует новые поля СИЗ.
    Adds and safely initializes new PPE fields.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(ppe_records);").fetchall()
    }
    if "provision_status" not in columns:
        connection.execute(
            "ALTER TABLE ppe_records ADD COLUMN provision_status TEXT NOT NULL DEFAULT 'legacy_not_tracked';"
        )
        connection.execute(
            """
            UPDATE ppe_records
            SET provision_status = CASE
                WHEN is_required = 1 AND is_issued = 0 THEN 'required_not_issued'
                WHEN is_required = 0 THEN 'not_required'
                ELSE 'issued'
            END;
            """
        )
    if "compliance_check_state" not in columns:
        connection.execute(
            "ALTER TABLE ppe_records ADD COLUMN compliance_check_state TEXT NOT NULL DEFAULT 'legacy_not_tracked';"
        )
    if "basis_text" not in columns:
        connection.execute("ALTER TABLE ppe_records ADD COLUMN basis_text TEXT NOT NULL DEFAULT '';")
    if "basis_note" not in columns:
        connection.execute("ALTER TABLE ppe_records ADD COLUMN basis_note TEXT NOT NULL DEFAULT '';")


def _ensure_medical_normative_columns(connection: Connection) -> None:
    """Добавляет новые поля медицины без ложных выводов по старым данным.
    Adds medical normative fields without false assumptions for legacy data.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(medical_records);").fetchall()
    }
    if "medical_exam_basis" not in columns:
        connection.execute(
            "ALTER TABLE medical_records ADD COLUMN medical_exam_basis TEXT NOT NULL DEFAULT 'legacy_not_tracked';"
        )
    if "basis_text" not in columns:
        connection.execute("ALTER TABLE medical_records ADD COLUMN basis_text TEXT NOT NULL DEFAULT '';")
    if "basis_note" not in columns:
        connection.execute("ALTER TABLE medical_records ADD COLUMN basis_note TEXT NOT NULL DEFAULT '';")


def _ensure_work_permit_target_training_columns(connection: Connection) -> None:
    """Добавляет поля целевого инструктажа и основания для нарядов-допусков.
    Adds targeted-training and basis fields for work permits.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(work_permits);").fetchall()
    }
    if "target_training_status" not in columns:
        connection.execute(
            "ALTER TABLE work_permits ADD COLUMN target_training_status TEXT NOT NULL DEFAULT 'legacy_not_tracked';"
        )
    if "target_training_date" not in columns:
        connection.execute(
            "ALTER TABLE work_permits ADD COLUMN target_training_date TEXT NOT NULL DEFAULT '';"
        )
    if "target_training_conducted_by" not in columns:
        connection.execute(
            "ALTER TABLE work_permits ADD COLUMN target_training_conducted_by TEXT NOT NULL DEFAULT '';"
        )
    if "target_training_note" not in columns:
        connection.execute(
            "ALTER TABLE work_permits ADD COLUMN target_training_note TEXT NOT NULL DEFAULT '';"
        )
    if "basis_text" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN basis_text TEXT NOT NULL DEFAULT '';")
    if "basis_note" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN basis_note TEXT NOT NULL DEFAULT '';")


def _ensure_work_permit_extension_columns(connection: Connection) -> None:
    """Додає поля первинного строку та одноразового продовження для нарядів-допусків.
    Adds base-term and one-time extension fields for work permits.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(work_permits);").fetchall()
    }
    if "base_ends_at" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN base_ends_at TEXT NOT NULL DEFAULT '';")
        connection.execute("UPDATE work_permits SET base_ends_at = ends_at WHERE base_ends_at = '';")
    if "extension_count" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN extension_count INTEGER NOT NULL DEFAULT 0;")
    if "extended_at" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN extended_at TEXT NULL;")
    if "extension_reason_text" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN extension_reason_text TEXT NOT NULL DEFAULT '';")


def _ensure_work_permit_reissue_columns(connection: Connection) -> None:
    """Додає поля перевипуску та зв'язку між старим і новим нарядами.
    Adds reissue fields and linkage between old and new permits.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(work_permits);").fetchall()
    }
    if "reissued_from_record_id" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN reissued_from_record_id INTEGER NULL;")
    if "reissued_to_record_id" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN reissued_to_record_id INTEGER NULL;")
    if "reissue_reason_text" not in columns:
        connection.execute("ALTER TABLE work_permits ADD COLUMN reissue_reason_text TEXT NOT NULL DEFAULT '';")


def _ensure_port_passports_r_base_column(connection: Connection) -> None:
    """Додає поле базового індексу ризику для динамічного контуру ПОРТ-Р.
    Adds the base risk index field for the PORT-R dynamic circuit.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(port_site_passports);").fetchall()
    }
    if "r_base" not in columns:
        connection.execute(
            "ALTER TABLE port_site_passports ADD COLUMN r_base REAL NOT NULL DEFAULT 1.0;"
        )


def _ensure_port_compensating_barriers_macrovariable_column(connection: Connection) -> None:
    """Додає прив'язку компенсуючого бар'єра до макрозмінної Т-П-С-В-Б.
    Adds macrovariable linkage for compensating barriers (T-P-S-V-B).
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(port_compensating_barriers);").fetchall()
    }
    if "macrovariable" not in columns:
        connection.execute(
            "ALTER TABLE port_compensating_barriers ADD COLUMN macrovariable TEXT NOT NULL DEFAULT 'B';"
        )


def _ensure_port_shift_checklist_barriers_table(connection: Connection) -> None:
    """Створює таблицю застосованих компенсуючих бар'єрів оцінки зміни та переносить legacy active_barrier_id.
    Creates the applied compensating-barriers junction table and migrates legacy active_barrier_id.
    """

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS port_shift_checklist_barriers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checklist_id INTEGER NOT NULL,
            barrier_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (checklist_id)
                REFERENCES port_shift_checklists(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (barrier_id)
                REFERENCES port_compensating_barriers(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
        """
    )
    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_port_shift_checklist_barriers_unique
        ON port_shift_checklist_barriers(checklist_id, barrier_id);
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_port_shift_checklist_barriers_checklist
        ON port_shift_checklist_barriers(checklist_id);
        """
    )
    connection.execute(
        """
        INSERT INTO port_shift_checklist_barriers (checklist_id, barrier_id)
        SELECT c.id, c.active_barrier_id
        FROM port_shift_checklists c
        WHERE c.active_barrier_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM port_shift_checklist_barriers cb
              WHERE cb.checklist_id = c.id AND cb.barrier_id = c.active_barrier_id
          );
        """
    )


def _ensure_app_settings_columns(connection: Connection) -> None:
    """Мігрує старий формат app_settings у поточну схему налаштувань.
    Migrates legacy app_settings layout into the current settings schema.
    """

    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(app_settings);").fetchall()
    }
    if "setting_key" in columns and "setting_value" in columns:
        return
    if not {"key", "value"}.issubset(columns):
        return

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS app_settings_v2 (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        INSERT OR REPLACE INTO app_settings_v2 (setting_key, setting_value)
        SELECT key, value
        FROM app_settings;

        DROP TABLE app_settings;

        ALTER TABLE app_settings_v2 RENAME TO app_settings;
        """
    )
