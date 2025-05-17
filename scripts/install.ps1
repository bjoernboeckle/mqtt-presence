$ErrorActionPreference = "Stop"

# Konfiguration
$AppName = "mqtt-presence"
$InstallDir = "$Env:ProgramData\$AppName"
$VenvDir = "$InstallDir\venv"
$Python = "python"
$ExePath = "$VenvDir\Scripts\mqtt-presence.exe"
$NssmPath = "$InstallDir\nssm.exe"
$ServiceName = $AppName
$NssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$TempZip = "$env:TEMP\nssm.zip"
$TempExtractDir = "$env:TEMP\nssm"

Write-Host "🏁 Starting installation/update of '$AppName'..."

# Installationsverzeichnis erstellen
Write-Host "📁 Creating installation directory at $InstallDir..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# NSSM herunterladen und entpacken (falls nicht vorhanden)
if (!(Test-Path $NssmPath)) {
    Write-Host "⬇️  Downloading NSSM..."
    Invoke-WebRequest -Uri $NssmUrl -OutFile $TempZip

    Write-Host "📦 Extracting NSSM..."
    Expand-Archive -Path $TempZip -DestinationPath $TempExtractDir -Force

    $nssmExe = Get-ChildItem -Path $TempExtractDir -Recurse -Filter "nssm.exe" |
        Where-Object { $_.FullName -like "*win64*" } |
        Select-Object -First 1

    if (!$nssmExe) {
        Write-Host "❌ Failed to extract nssm.exe"
        exit 1
    }

    Copy-Item $nssmExe.FullName -Destination $NssmPath -Force
    Remove-Item -Recurse -Force $TempExtractDir
    Remove-Item -Force $TempZip
}

# Virtuelle Umgebung erstellen
if (!(Test-Path "$VenvDir\Scripts\Activate.ps1")) {
    Write-Host "🐍 Creating virtual environment..."
    & $Python -m venv "$VenvDir"
}

# Installation / Update von mqtt-presence
Write-Host "⬆️  Installing or upgrading mqtt-presence..."
& "$VenvDir\Scripts\pip.exe" install --upgrade pip
& "$VenvDir\Scripts\pip.exe" install --upgrade mqtt-presence

# Dienst stoppen, falls aktiv
try {
    $status = & $NssmPath status $ServiceName 2>$null
    if ($status -and $status -match "SERVICE_RUNNING") {
        Write-Host "🛑 Stopping existing service..."
        & $NssmPath stop $ServiceName confirm | Out-Null
        Start-Sleep -Seconds 2
    }
} catch {
    Write-Host "Info: Service '$ServiceName' nicht gefunden oder nicht laufend."
}

# Dienst erstellen oder aktualisieren
if (-not (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)) {
    Write-Host "🛠️  Creating new Windows service '$ServiceName'..."
    & $NssmPath install $ServiceName $ExePath
    & $NssmPath set $ServiceName AppDirectory $InstallDir
    & $NssmPath set $ServiceName AppParameters "--data ./data --log ./log"
    & $NssmPath set $ServiceName Start SERVICE_AUTO_START
    & $NssmPath set $ServiceName AppExit Default Restart
} else {
    Write-Host "🔁 Updating existing Windows service '$ServiceName'..."
    & $NssmPath set $ServiceName Application $ExePath
    & $NssmPath set $ServiceName AppDirectory $InstallDir
    & $NssmPath set $ServiceName AppParameters "--data ./data --log ./log"
}

# Dienst starten
Write-Host "🚀 Starting service..."
& $NssmPath start $ServiceName | Out-Null

Write-Host "✅ Installation complete. Service is running as '$ServiceName'."
