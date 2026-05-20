#define MyAppName "ClearWork"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "ClearWork"
#define MyAppExeName "ClearWork.exe"
#define MyAppSourceDir "..\dist\ClearWork"
#define MyAppIcon "..\src\osah\ui\qt\assets\icons\clearwork.ico"

[Setup]
AppId={{6E5E9F0D-1D02-4A56-82CC-4C1F40F3EE41}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\ClearWork
DefaultGroupName=ClearWork
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=ClearWork-Setup-0.1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "data\*,logs\*"

[Icons]
Name: "{group}\ClearWork"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\ClearWork"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch ClearWork"; Flags: nowait postinstall skipifsilent
