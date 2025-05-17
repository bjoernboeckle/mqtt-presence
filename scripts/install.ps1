$ErrorActionPreference = "Stop"

$AppName = "mqtt-presence"
$InstallDir = "$Env:ProgramData\$AppName"
$VenvDir = "$InstallDir\venv"
$Python = "python"
$ExePath = "$VenvDir\Scripts\mqtt-presence.exe"
$VbsLauncher = "$InstallDir\launch.vbs"
$TaskName = "$AppName"

# Stoppe existierenden Task, falls vorhanden
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "🛑 Stopping existing scheduled task '$TaskName'..."
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Write-Host "[1/6] Creating installation directory at $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

Write-Host "[2/6] Creating virtual environment"
& $Python -m venv "$VenvDir"

Write-Host "[3/6] Installing mqtt-presence"
& "$VenvDir\Scripts\pip.exe" install --upgrade pip
& "$VenvDir\Scripts\pip.exe" install mqtt-presence

Write-Host "[4/6] Creating invisible launch wrapper (launch.vbs)"
$VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "$ExePath" & chr(34), 0
"@
Set-Content -Path $VbsLauncher -Value $VbsContent

Write-Host "[5/6] Creating scheduled task for autostart"
$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsLauncher`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -TaskName $TaskName -Force

Write-Host "[6/6] Launching mqtt-presence in the background..."
Start-Process "wscript.exe" "`"$VbsLauncher`""

Write-Host "✅ Installation completed. Service is now running in the background."
