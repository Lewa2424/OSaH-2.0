# ClearWork

Інструкція для користувача підприємства: [docs/ClearWork_користувач.md](docs/ClearWork_користувач.md)

ClearWork is a local desktop system for occupational safety workflows.

The active production UI is built on `PySide6` / Qt and works against a local `SQLite` database. The repository still contains a legacy `CustomTkinter` desktop layer in `src/osah/ui/desktop/`, but it is kept only for reference and migration support. The current working launch path goes through the Qt application. The internal service/package name remains `osah`.

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
- Version source: `src/osah/version.py`
- Local data directory: `data/`
- Local logs directory: `logs/`

## Installation (development)

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

Source runs enable demo seed by default; disable with `OSAH_DISABLE_DEMO_SEED=1`. Setup key is skipped in development runs (`not sys.frozen`).

## Tests

```powershell
pytest
```

## Distribution (installers)

Production and demo Windows installers:

```powershell
powershell -ExecutionPolicy Bypass -File installer\build_clearwork.ps1
powershell -ExecutionPolicy Bypass -File installer_DEMO\build_clearwork.ps1
```

Outputs (local, not committed — `*.exe` in `.gitignore`):

- `installer\ClearWork-Setup-1.1.3.exe`
- `installer_DEMO\ClearWork-Demo-Setup-1.1.3.exe`

The build scripts also generate `installer\ClearWork_швидкий_старт.pdf` (client quick-start, bundled into installers).

### Setup keys (developer)

- Key Admin: `tools/clearwork_key_admin/` — see [tools/clearwork_key_admin/README.md](tools/clearwork_key_admin/README.md)
- Pilot / install checklist: [docs/ClearWork_чеклист_встановлення.md](docs/ClearWork_чеклист_встановлення.md)
- Windows install notes: [docs/INSTALL_WINDOWS.md](docs/INSTALL_WINDOWS.md)

## Notes

- `CustomTkinter` is not the main UI stack anymore.
- Build artifacts such as `build/` and `dist/` are not part of the active source architecture.
