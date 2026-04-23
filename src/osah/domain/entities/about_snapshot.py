from dataclasses import dataclass


@dataclass(slots=True)
class AboutSnapshot:
    """About screen data."""

    product_name: str
    app_version: str
    ui_status: str
    operation_model: str
    database_path: str
    data_directory_path: str
    log_path: str
    table_count: int
    employee_count: int
    unread_news_count: int
    branch_name: str
