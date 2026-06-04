param(
    [string]$PythonExe = "C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe",
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

$pyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "osah.spec"
)

Write-Host "Building ClearWork executable..."
& $PythonExe @pyInstallerArgs

$runtimeArtifacts = @(
    (Join-Path $ProjectRoot "dist\\ClearWork\\data"),
    (Join-Path $ProjectRoot "dist\\ClearWork\\logs")
)

foreach ($artifactPath in $runtimeArtifacts) {
    if (Test-Path $artifactPath) {
        Write-Host "Removing runtime artifact from dist: $artifactPath"
        Remove-Item -LiteralPath $artifactPath -Recurse -Force
    }
}

$isccCandidates = @(
    "C:\Users\User\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files (Inno Setup 6)\ISCC.exe"
)
$isccPath = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $isccPath) {
    throw "Inno Setup compiler (ISCC.exe) not found. Install Inno Setup 6 and rerun installer/build_clearwork.ps1."
}

Write-Host "Building ClearWork installer..."
& $isccPath (Join-Path $PSScriptRoot "ClearWork.iss")
