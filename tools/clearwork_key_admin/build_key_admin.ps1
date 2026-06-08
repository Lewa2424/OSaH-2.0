param(
    [string]$PythonExe = "C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Building portable ClearWorkKeyAdmin.exe..."
& $PythonExe -m PyInstaller --noconfirm --clean "key_admin.spec"

$builtExe = Join-Path $ProjectRoot "dist\ClearWorkKeyAdmin.exe"
$targetExe = Join-Path $ProjectRoot "ClearWorkKeyAdmin.exe"

if (-not (Test-Path $builtExe)) {
    throw "Build failed: $builtExe not found."
}

Copy-Item -LiteralPath $builtExe -Destination $targetExe -Force
Write-Host "Portable exe ready: $targetExe"
