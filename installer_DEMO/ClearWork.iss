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
DisableDirPage=no
DisableProgramGroupPage=yes
LicenseFile=license_uk.txt
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=ClearWork-Setup-0.1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
UsePreviousAppDir=yes

[Languages]
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Tasks]
Name: "desktopicon"; Description: "Створити ярлик на стільниці"; GroupDescription: "Додаткові ярлики:"; Flags: unchecked

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "data\*,logs\*"

[Icons]
Name: "{group}\ClearWork"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\ClearWork"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустити ClearWork"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeUninstall: Boolean;
begin
  Result :=
    MsgBox(
      'Ви збираєтеся видалити ClearWork.' + #13#10#13#10 +
      'Програма буде видалена, але робочі дані можуть залишатися у папці встановлення.' + #13#10 +
      'Якщо після цього вручну видалити папку ClearWork, база даних, журнали та резервні копії можуть бути втрачені.' + #13#10#13#10 +
      'Перед видаленням рекомендується створити резервну копію у програмі.' + #13#10#13#10 +
      'Продовжити видалення?',
      mbConfirmation,
      MB_YESNO
    ) = idYes;
end;
