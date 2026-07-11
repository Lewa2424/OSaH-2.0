#define MyAppName "ClearWork Demo"
#define MyAppVersion "1.1.3"
#define MyAppPublisher "ClearWork"
#define MyAppExeName "ClearWork.exe"
#define MyAppSourceDir "..\dist\ClearWork"
#define MyAppIcon "..\src\osah\ui\qt\assets\icons\clearwork.ico"

[Setup]
AppId={{A4C2D8F1-9B3E-4F71-A6D2-1E8C5B0D4F92}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\ClearWork
DefaultGroupName=ClearWork Demo
DisableDirPage=no
DisableProgramGroupPage=yes
LicenseFile=license_uk.txt
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=ClearWork-Demo-Setup-1.1.3
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
Source: "..\installer\ClearWork_швидкий_старт.pdf"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\installer\GettingStarted_uk.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ClearWork Demo"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Інструкція ClearWork"; Filename: "{app}\ClearWork_швидкий_старт.pdf"
Name: "{autodesktop}\ClearWork Demo"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\ClearWork_швидкий_старт.pdf"; Description: "Відкрити інструкцію"; Flags: postinstall shellexec skipifsilent
Filename: "{app}\{#MyAppExeName}"; Description: "Запустити ClearWork Demo"; Flags: nowait postinstall skipifsilent unchecked

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  DemoMarkerPath: String;
  DemoTimedMarkerPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    DemoMarkerPath := ExpandConstant('{app}\ClearWork.demo');
    DemoTimedMarkerPath := ExpandConstant('{app}\ClearWork.demo_timed');
    SaveStringToFile(DemoMarkerPath, 'demo', False);
    SaveStringToFile(DemoTimedMarkerPath, 'timed', False);
  end;
end;

function InitializeUninstall: Boolean;
begin
  Result :=
    MsgBox(
      'Ви збираєтеся видалити ClearWork Demo.' + #13#10#13#10 +
      'Програма буде видалена, але робочі дані можуть залишатися у папці встановлення (data\, logs\, резервні копії).' + #13#10 +
      'Перед видаленням рекомендується створити резервну копію у програмі.' + #13#10#13#10 +
      'Важливо: демонстраційний період (48 годин) зберігається у папці data\.' + #13#10 +
      'Якщо видалити data\, таймер і демо-дані будуть скинуті.' + #13#10#13#10 +
      'Продовжити видалення?',
      mbConfirmation,
      MB_YESNO
    ) = idYes;
end;
