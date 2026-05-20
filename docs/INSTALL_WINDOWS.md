# ClearWork Windows Installation

## What gets installed

`ClearWork-Setup-0.1.0.exe` installs ClearWork locally for the current Windows user.

- Application folder: `%LOCALAPPDATA%\Programs\ClearWork`
- Start Menu shortcut: `ClearWork`
- Optional desktop shortcut: `ClearWork`

Python does not need to be installed separately.

## Installation steps

1. Download `ClearWork-Setup-0.1.0.exe` from the official ClearWork release.
2. Run the installer.
3. If Windows SmartScreen shows a warning:
   - click `More info`
   - click `Run anyway`
4. Follow the installer wizard.
5. Launch ClearWork from the Start Menu or desktop shortcut.

## SmartScreen warning

Windows may warn about newly built unsigned applications.

ClearWork is packaged without a paid code-signing certificate in this release flow.  
If the file was obtained from the official ClearWork release, you can use:

- `More info`
- `Run anyway`

## First launch

On the first launch, ClearWork opens the local security setup screen and creates its working data folders automatically.

## Where user data is stored

ClearWork uses a local on-device database and stores working data relative to the installed application folder:

- `data\`
- `logs\`
- `data\backups\`
- `data\recovery\`

If the application is launched normally, these folders are created automatically.

## How to uninstall

You can remove ClearWork using one of these options:

1. Windows Settings -> Apps -> Installed apps -> `ClearWork` -> `Uninstall`
2. Run the uninstaller directly from:
   - `%LOCALAPPDATA%\Programs\ClearWork\unins000.exe`

By default, uninstall removes the program files and shortcuts, but leaves user-created working data in place:

- `%LOCALAPPDATA%\Programs\ClearWork\data`
- `%LOCALAPPDATA%\Programs\ClearWork\logs`

If a full cleanup is required, delete these folders manually after uninstall.

## If the program does not start

1. Make sure the installation finished without errors.
2. Launch ClearWork once directly from:
   - `%LOCALAPPDATA%\Programs\ClearWork\ClearWork.exe`
3. Check whether the folders below were created:
   - `%LOCALAPPDATA%\Programs\ClearWork\data`
   - `%LOCALAPPDATA%\Programs\ClearWork\logs`
4. If SmartScreen blocked the launch, reopen the file and use:
   - `More info`
   - `Run anyway`
5. If the problem persists, collect:
   - a screenshot of the error
   - contents of `logs\osah.log`

## Packaging note

This Windows installer is built with:

- `PyInstaller`
- `Inno Setup 6`

The current `0.1.0` installer is the first unsigned Windows build prepared for manual testing and early distribution. Windows may show SmartScreen warnings because this version is not signed with a paid code-signing certificate.
