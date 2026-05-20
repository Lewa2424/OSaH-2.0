# OSaH 2.0

OSaH 2.0 is a local desktop system for occupational safety workflows.

The active production UI is built on `PySide6` / Qt and works against a local `SQLite` database. The repository still contains a legacy `CustomTkinter` desktop layer in `src/osah/ui/desktop/`, but it is kept only for reference and migration support. The current working launch path goes through the Qt application.

## Stack

- Python 3.12+
- PySide6 / Qt
- SQLite
- Clean Architecture / DDD-style modular structure

## Project State

- Active UI: `src/osah/ui/qt/`
- Legacy desktop UI: `src/osah/ui/desktop/`
- Entry point: `main.py`
- Application bootstrap: `src/osah/main.py`
- Local data directory: `data/`
- Local logs directory: `logs/`

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

If you need tests and legacy desktop imports in the local environment, install dev dependencies:

```powershell
pip install -r requirements-dev.txt
```

## Run

Run the project from the repository root:

```powershell
python main.py
```

`main.py` adds `src/` to `sys.path` and starts the application through `osah.main.main()`.

## Tests

Basic test command:

```powershell
pytest
```

If your environment still contains legacy or transitional tests that are being adapted, you can run profile-specific checks instead, for example:

```powershell
pytest tests/test_date_helpers.py -q
```

## Notes

- `CustomTkinter` is not the main UI stack anymore. It remains only because the legacy desktop UI is still present in the repository.
- `pyproject.toml` was intentionally left unchanged at this step.
- Build artifacts such as `build/` and `dist/` are not part of the active source architecture.
