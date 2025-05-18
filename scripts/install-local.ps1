$ErrorActionPreference = "Stop"

# Konfiguration
$AppName = "mqtt-presence"
$LocalSource = "C:\source\python\mqtt-presence"  # << Pfad zu deinem lokalen Projekt
$InstallDir = "$Env:ProgramData\$AppName"
$VenvDir = "$InstallDir\venv"
$Python = "python"
$ExePath = "$VenvDir\Scripts\mqtt-presence.exe"
$NssmPath = "$InstallDir\nssm.exe"
$ServiceName = $AppName
$NssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$TempZip = "$env:TEMP\nssm.zip"
$TempExtractDir = "$env:TEMP\nssm"

Write-Host "Starting local development installation of '$AppName'..."

# Installationsverzeichnis vorbereiten
Write-Host "Creating or updating $InstallDir..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# NSSM herunterladen und entpacken
if (!(Test-Path $NssmPath)) {
    Write-Host "Downloading NSSM..."
    Invoke-WebRequest -Uri $NssmUrl -OutFile $TempZip
    Expand-Archive -Path $TempZip -DestinationPath $TempExtractDir -Force

    $nssmExe = Get-ChildItem -Path $TempExtractDir -Recurse -Filter "nssm.exe" |
        Where-Object { $_.FullName -like "*win64*" } |
        Select-Object -First 1

    if (!$nssmExe) {
        Write-Host "Failed to extract nssm.exe"
        exit 1
    }

    Copy-Item $nssmExe.FullName -Destination $NssmPath -Force
    Remove-Item -Recurse -Force $TempExtractDir, $TempZip
}

# Virtuelle Umgebung erstellen
if (!(Test-Path "$VenvDir\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..."
    & $Python -m venv "$VenvDir"
}

# Lokalen Source-Code kopieren
Write-Host "Copying local mqtt-presence code to $InstallDir..."
Copy-Item -Path "$LocalSource\*" -Destination $InstallDir -Recurse -Force

# Installation im editable/development-Modus
Write-Host "Installing mqtt-presence (editable) from local source..."
& "$VenvDir\Scripts\pip.exe" install --upgrade pip
& "$VenvDir\Scripts\pip.exe" install -e "$InstallDir"

# Dienst stoppen, falls laufend
try {
    $status = & $NssmPath status $ServiceName 2>$null
    if ($status -and $status -match "SERVICE_RUNNING") {
        Write-Host "Stopping existing service..."
        & $NssmPath stop $ServiceName confirm | Out-Null
        Start-Sleep -Seconds 2
    }
} catch {
    Write-Host "Service not found or not running."
}

# Dienst (neu) registrieren
Write-Host "Registering service '$ServiceName'..."

# Argumente für Konfiguration (z. B. Relativpfade unterhalb von ProgramData)
$dataArg = "--data `"$InstallDir\data`""
$logArg = "--log `"$InstallDir\log`""

if (-not (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)) {
    & $NssmPath install $ServiceName $ExePath $dataArg $logArg
    & $NssmPath set $ServiceName AppDirectory $InstallDir
    & $NssmPath set $ServiceName Start SERVICE_AUTO_START
    & $NssmPath set $ServiceName AppExit Default Restart
} else {
    & $NssmPath set $ServiceName Application $ExePath
    & $NssmPath set $ServiceName AppDirectory $InstallDir
    & $NssmPath set $ServiceName AppParameters "$dataArg $logArg"
}

# Dienst starten
Write-Host "🚀 Starting service..."
& $NssmPath start $ServiceName | Out-Null

Write-Host "Service '$ServiceName' is now running from local code."
