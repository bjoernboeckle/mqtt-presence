$AppName = "mqtt-presence"
$InstallDir = "$Env:ProgramData\$AppName"
$TaskName = $AppName
$ConfigDir = "$Env:APPDATA\$AppName"
$LogDir    = "$Env:LOCALAPPDATA\$AppName"

Write-Host "[1/4] Stopping any running processes..."
Get-Process mqtt-presence -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "[2/4] Removing scheduled task..."
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Write-Host "[3/4] Deleting installation directory ($InstallDir)..."
Remove-Item -Recurse -Force -Path "$InstallDir" -ErrorAction SilentlyContinue

Write-Host "[4/4] Removing configuration and log data..."
Remove-Item -Recurse -Force -Path "$ConfigDir" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -Path "$LogDir" -ErrorAction SilentlyContinue

Write-Host "Uninstallation completed."
