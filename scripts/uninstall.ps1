$ErrorActionPreference = "Stop"

$AppName = "mqtt-presence"
$ServiceName = $AppName

# NSSM Pfad (angenommen aus Installation)
$InstallDir = "$Env:ProgramData\$AppName"
$NssmPath = "$InstallDir\nssm.exe"


Write-Host "🛑 Stopping and removing service '$ServiceName' if exists..."

try {
    if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
        if ($NssmPath -and (Test-Path $NssmPath)) {
            & $NssmPath stop $ServiceName confirm | Out-Null
            Start-Sleep -Seconds 2
            & $NssmPath remove $ServiceName confirm | Out-Null
        } else {
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            sc.exe delete $ServiceName | Out-Null
        }
        Write-Host "✅ Service removed."
    } else {
        Write-Host "Info: Service '$ServiceName' not found."
    }
} catch {
    Write-Warning "Error removing service: $_"
}

if (Test-Path $InstallDir) {
    Write-Host "🗑️ Deleting installation directory: $InstallDir"
    Remove-Item -Recurse -Force -Path $InstallDir -ErrorAction SilentlyContinue
}

Write-Host "✅ Uninstallation complete."
