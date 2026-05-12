# OSaH 2.0

OSaH 2.0 is a local desktop system for occupational safety workflows. The current production UI is based on `PySide6` and runs entirely on a local SQLite database without a server dependency.

## What The Project Does

The system consolidates the main safety-control areas into one desktop application:

- employee registry and readiness overview;
- training records and status tracking;
- PPE accounting and control status;
- medical examination tracking;
- work permit management;
- contractor registry;
- daily reports and mail settings;
- news / regulatory source monitoring;
- backups, audit log, archive, and security settings.

## Current State

- Primary frontend: `src/osah/ui/qt/`
- Legacy frontend kept as reference only: `src/osah/ui/desktop/`
- Main entry point: `main.py`
- Application bootstrap: `src/osah/main.py`
- Local data directory: `data/`
- Local logs directory: `logs/`
- Runtime database path: `data/osah.sqlite3`

The repository still contains the older `CustomTkinter` layer, but the active application startup path goes through the secured Qt shell.

## Architecture

The project follows a modular layered structure:

- `src/osah/domain`  
  Domain entities and pure business rules.

- `src/osah/application`  
  Use-case services that orchestrate domain logic and infrastructure access.

- `src/osah/infrastructure`  
  SQLite access, logging, backup, import, security, and external I/O.

- `src/osah/ui/qt`  
  Active Qt user interface, routing, screens, components, workers, and design tokens.

- `src/osah/ui/desktop`  
  Deprecated desktop layer retained only as migration/reference material.

- `tests`  
  Automated regression coverage for application, domain, and UI-adjacent behavior.

The application bootstrap initializes storage, logging, schema, demo seed data, notifications, security baseline, and startup backup before opening the UI.

## Main UI Sections

The current Qt shell routes between these sections:

- Dashboard
- Employees
- Trainings
- PPE
- Medical
- Work Permits
- Contractors
- Archive
- Reports
- News / NPA
- Settings
- About

## Security Flow

The application starts with a mandatory security flow:

1. First launch initializes the security baseline.
2. If access is not configured yet, the initial setup screen is shown.
3. On subsequent launches, the login screen is shown with role-based access.
4. Recovery flow is available for access reset scenarios.
5. After authentication, the main Qt shell is opened.

The secured startup path is implemented through `src/osah/ui/qt/run_qt_application_secured.py`.

## Running The Project

Requirements:

- Python `3.12+`
- `PySide6`

From the repository root:

```bash
python main.py
```

At startup the app creates required local directories if they do not exist:

- `data/`
- `logs/`

## Tests

The repository currently contains `67` test files under `tests/`.

If your environment already has the required dependencies installed, run:

```bash
python -m pytest tests
```

If `pytest` is not available in the environment, use the project test runner standard adopted in your local setup.

## Packaging

The repository includes a PyInstaller spec:

```bash
pyinstaller osah.spec
```

The spec is configured for the Qt application and bundles:

- Qt design resources;
- Qt assets;
- required application modules;
- a windowed executable named `OSaH`.

## Important Notes

- `README` content was aligned to the current codebase state, not the old marketing description.
- `src/osah/ui/desktop/` should not be used for new feature development.
- Existing build artifacts in `build/` and `dist/` are generated outputs, not source architecture.
- The repository currently has unrelated working-tree changes outside this `README` update; they were intentionally left untouched.
