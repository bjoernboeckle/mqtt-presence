$ErrorActionPreference = "Stop"

$AppName = "mqtt-presence"
$InstallDir = "$Env:ProgramData\$AppName"
$VenvDir = "$InstallDir\venv"
$Python = "python"
$ExePath = "$VenvDir\Scripts\mqtt-presence.exe"
$VbsLauncher = "$InstallDir\launch.vbs"
$TaskName = "$AppName"

Write-Host "[1/5] Creating installation directory at $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

Write-Host "[2/5] Creating virtual environment"
& $Python -m venv "$VenvDir"

Write-Host "[3/5] Installing mqtt-presence"
& "$VenvDir\Scripts\pip.exe" install --upgrade pip
& "$VenvDir\Scripts\pip.exe" install mqtt-presence

Write-Host "[4/5] Creating invisible launch wrapper (launch.vbs)"
Set-Content -Path $VbsLauncher -Value "Set WshShell = CreateObject(""WScript.Shell"")`nWshShell.Run chr(34) & ""$ExePath"" & chr(34), 0"

Write-Host "[5/5] Creating scheduled task for autostart"
$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsLauncher`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -TaskName $TaskName -Force

Write-Host "🚀 Launching mqtt-presence in the background..."
Start-Process "wscript.exe" "`"$VbsLauncher`""

Write-Host "✅ Installation completed. Service is now running in the background."
