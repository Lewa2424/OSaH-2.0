import subprocess
import tomllib
from pathlib import Path

from osah.domain.entities.about_snapshot import AboutSnapshot
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.count_employees import count_employees
from osah.infrastructure.database.queries.count_unread_news_items import count_unread_news_items
from osah.infrastructure.database.queries.list_user_table_names import list_user_table_names


# ###### ЗАВАНТАЖЕННЯ ІНФОРМАЦІЇ "ПРО ПРОГРАМУ" / LOAD ABOUT SNAPSHOT ######
def load_about_snapshot(database_path: Path, log_path: Path) -> AboutSnapshot:
    """Loads service/product metadata for About screen."""

    connection = create_database_connection(database_path)
    try:
        employee_total = count_employees(connection)
        unread_news_total = count_unread_news_items(connection)
        table_total = len(list_user_table_names(connection))
    finally:
        connection.close()

    return AboutSnapshot(
        product_name="OSaH 2.0",
        app_version=_read_app_version(),
        ui_status="Qt industrial control contour",
        operation_model="Local single-operator desktop with isolated external contour",
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
    """Reads project version from pyproject.toml."""

    project_root = Path(__file__).resolve().parents[4]
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return "0.1.0"
    content = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project_data = content.get("project")
    if isinstance(project_data, dict):
        value = project_data.get("version")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "0.1.0"


# ###### ВИЗНАЧЕННЯ ГІЛКИ РЕПОЗИТОРІЮ / RESOLVE REPOSITORY BRANCH ######
def _resolve_branch_name(workspace_path: Path) -> str:
    """Resolves git branch name when repository metadata is available."""

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=workspace_path,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:  # noqa: BLE001
        return "unknown"
    branch_name = completed.stdout.strip()
    return branch_name or "unknown"
