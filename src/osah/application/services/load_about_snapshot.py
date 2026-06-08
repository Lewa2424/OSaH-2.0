import subprocess
from pathlib import Path

from osah.domain.entities.about_snapshot import AboutSnapshot
from osah.version import __version__
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.count_employees import count_employees
from osah.infrastructure.database.queries.count_unread_news_items import count_unread_news_items
from osah.infrastructure.database.queries.list_user_table_names import list_user_table_names


# ###### ЗАВАНТАЖЕННЯ ІНФОРМАЦІЇ "ПРО ПРОГРАМУ" / LOAD ABOUT SNAPSHOT ######
def load_about_snapshot(database_path: Path, log_path: Path) -> AboutSnapshot:
    """Загружает служебные данные для экрана «О программе».
    Loads service metadata for the About screen.
    """

    connection = create_database_connection(database_path)
    try:
        employee_total = count_employees(connection)
        unread_news_total = count_unread_news_items(connection)
        table_total = len(list_user_table_names(connection))
    finally:
        connection.close()

    return AboutSnapshot(
        product_name="ClearWork",
        app_version=_read_app_version(),
        ui_status="локальний робочий інтерфейс на Qt",
        operation_model="локальна настільна система з ізольованим зовнішнім контуром",
        database_path=str(database_path),
        data_directory_path=str(database_path.parent),
        log_path=str(log_path),
        table_count=table_total,
        employee_count=employee_total,
        unread_news_count=unread_news_total,
        branch_name=_resolve_branch_name(database_path.parent),
    )


# ###### ЧИТАННЯ ВЕРСІЇ ПРОЄКТУ / READ PROJECT VERSION ######
def _read_app_version() -> str:
    """Повертає версію ClearWork з osah.version.
    Returns the ClearWork version from osah.version.
    """

    return __version__


# ###### ВИЗНАЧЕННЯ ГІЛКИ РЕПОЗИТОРІЮ / RESOLVE REPOSITORY BRANCH ######
def _resolve_branch_name(workspace_path: Path) -> str:
    """Определяет имя текущей git-ветки, если метаданные репозитория доступны.
    Resolves the current git branch name when repository metadata is available.
    """

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=workspace_path,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:  # noqa: BLE001
        return "невідомо"
    branch_name = completed.stdout.strip()
    return branch_name or "невідомо"
