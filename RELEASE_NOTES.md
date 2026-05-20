# Release Notes

## ClearWork v0.1.0

### First installer build

- First Windows installer build prepared for manual testing and early delivery
- Windows desktop executable packaged as `ClearWork.exe`
- Windows installer packaged as `ClearWork-Setup-0.1.0.exe`
- Installation works without requiring Python to be installed separately
- Per-user installation target: `%LOCALAPPDATA%\Programs\ClearWork`

### Data and runtime behavior

- ClearWork uses a local SQLite database stored in the application working folders
- Working folders are created locally on first launch:
  - `data\`
  - `logs\`
  - `data\backups\`
- Uninstall removes program files and shortcuts, but keeps user-created data and logs

### Branding and packaging

- Application icon unified around `clearwork.ico`
- User-facing product name aligned with `ClearWork`
- Installer and packaging metadata aligned with `ClearWork`

### Notes

- Internal package/module name remains `osah`
- This release flow is unsigned and may trigger Windows SmartScreen warnings
- SmartScreen warnings are expected because the installer is not signed with a paid code-signing certificate
