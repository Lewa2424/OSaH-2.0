#define MyAppName "ClearWork"
#define MyAppVersion "0.8.3"
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
OutputBaseFilename=ClearWork-Setup-0.8.3
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
Name: "demomode"; Description: "Демонстраційний режим (засів демонстраційних даних при першому запуску). Для робочої установки не вмикайте. Щоб вимкнути після помилки — перевстановіть без цієї галочки; папку data\ може знадобитися видалити вручну."; GroupDescription: "Режим установки:"; Flags: unchecked
Name: "desktopicon"; Description: "Створити ярлик на стільниці"; GroupDescription: "Додаткові ярлики:"; Flags: unchecked

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "data\*,logs\*"
Source: "GettingStarted_uk.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\ClearWork_користувач.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ClearWork"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\ClearWork"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустити ClearWork"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  DemoMarkerPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    DemoMarkerPath := ExpandConstant('{app}\ClearWork.demo');
    if IsTaskSelected('demomode') then
      SaveStringToFile(DemoMarkerPath, 'demo', False)
    else
    begin
      if FileExists(DemoMarkerPath) then
        DeleteFile(DemoMarkerPath);
    end;
  end;
end;

function InitializeUninstall: Boolean;
begin
  Result :=
    MsgBox(
      'Ви збираєтеся видалити ClearWork.' + #13#10#13#10 +
      'Програма буде видалена, але робочі дані можуть залишатися у папці встановлення (data\, logs\, резервні копії).' + #13#10 +
      'Перед видаленням рекомендується створити резервну копію у програмі.' + #13#10#13#10 +
      'Важливо про ключ установки:' + #13#10 +
      'ID установки зберігається у папці data\, а не в комп''ютері як такому.' + #13#10 +
      'Якщо видалити data\, з''явиться новий ID і старий ключ установки вже не підійде.' + #13#10 +
      'Для переустановки на тому ж ПК не видаляйте папку data\.' + #13#10#13#10 +
      'Продовжити видалення?',
      mbConfirmation,
      MB_YESNO
    ) = idYes;
end;
