$ErrorActionPreference = "Stop"

$AppName = "mqtt-presence"
$ServiceName = $AppName

# NSSM path (assumed from installation)
$InstallDir = "$Env:ProgramData\$AppName"
$NssmPath = "$InstallDir\nssm.exe"

function Log-Info($msg) {
    Write-Host "[INFO] $msg"
}
function Log-Warning($msg) {
    Write-Warning "[WARNING] $msg"
}
function Log-Error($msg) {
    Write-Error "[ERROR] $msg"
}

Log-Info "Stopping and removing service '$ServiceName' if it exists..."

try {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        if ($NssmPath -and (Test-Path $NssmPath)) {
            Log-Info "Using NSSM at '$NssmPath' to stop and remove the service."
            & $NssmPath stop $ServiceName confirm | Out-Null
            Start-Sleep -Seconds 2
            & $NssmPath remove $ServiceName confirm | Out-Null
            Log-Info "Service '$ServiceName' stopped and removed via NSSM."
        } else {
            Log-Warning "NSSM not found at '$NssmPath', falling back to native service commands."
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            sc.exe delete $ServiceName | Out-Null
            Log-Info "Service '$ServiceName' stopped and deleted via native commands."
        }
    } else {
        Log-Info "Service '$ServiceName' not found, skipping removal."
    }
} catch {
    Log-Error "Failed to remove service: $_"
}

if (Test-Path $InstallDir) {
    try {
        Log-Info "Deleting installation directory: $InstallDir"
        Remove-Item -Recurse -Force -Path $InstallDir -ErrorAction Stop
        Log-Info "Installation directory deleted."
    } catch {
        Log-Warning "Failed to delete installation directory: $_"
    }
} else {
    Log-Info "Installation directory '$InstallDir' does not exist, nothing to delete."
}

Log-Info "Uninstallation complete."
