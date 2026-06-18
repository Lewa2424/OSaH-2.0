from enum import StrEnum


class AiSemanticIntent(StrEnum):
    """Смысловое намерение AI-команды до привязки к текущим сервисам.
    Semantic AI intent before binding it to current services.
    """

    CREATE_EMPLOYEE = "create_employee"
    UPDATE_EMPLOYEE_SITE_BATCH = "update_employee_site_batch"
    PREPARE_EMPLOYEE_DATA_CLEANUP = "prepare_employee_data_cleanup"
    CREATE_TRAINING_RECORD = "create_training_record"
    CREATE_TRAINING_BATCH = "create_training_batch"
    CREATE_TARGET_TRAINING_FOR_WORK_PERMIT = "create_target_training_for_work_permit"
    CREATE_PPE_ISSUANCE = "create_ppe_issuance"
    CREATE_PPE_ISSUANCE_FOR_WORK_PERMIT_PARTICIPANTS = "create_ppe_issuance_for_work_permit_participants"
    REPLACE_PPE_ITEM = "replace_ppe_item"
    CREATE_OR_UPDATE_MEDICAL_RECORD = "create_or_update_medical_record"
    UPDATE_MEDICAL_RESTRICTION = "update_medical_restriction"
    UPDATE_MEDICAL_BATCH = "update_medical_batch"
    CREATE_WORK_PERMIT_DRAFT = "create_work_permit_draft"
    UPDATE_WORK_PERMIT_PARTICIPANTS = "update_work_permit_participants"
    ADD_WORK_PERMIT_SAFETY_MEASURES = "add_work_permit_safety_measures"
    UNKNOWN = "unknown"
