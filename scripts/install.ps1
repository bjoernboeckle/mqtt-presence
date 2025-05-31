$ErrorActionPreference = "Stop"

# Configuration
$serviceName = "mqtt-presence"
$programData = $env:ProgramData
$installDir = Join-Path $programData $serviceName
$NssmPath = "$InstallDir\nssm.exe"
$NssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$TempZip = "$env:TEMP\nssm.zip"
$TempExtractDir = "$env:TEMP\nssm"

$configArg = "--config `"$InstallDir\config`""
$logArg = "--log `"$InstallDir\log`""

# 1. Create installation directory
Write-Host "Creating installation directory at $InstallDir..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# 2. Download and extract NSSM if not present
if (!(Test-Path $NssmPath)) {
    Write-Host "Downloading NSSM..."
    Invoke-WebRequest -Uri $NssmUrl -OutFile $TempZip

    Write-Host "Extracting NSSM..."
    Expand-Archive -Path $TempZip -DestinationPath $TempExtractDir -Force

    $nssmExe = Get-ChildItem -Path $TempExtractDir -Recurse -Filter "nssm.exe" |
        Where-Object { $_.FullName -like "*win64*" } |
        Select-Object -First 1

    if (!$nssmExe) {
        Write-Host "Failed to extract nssm.exe"
        exit 1
    }

    Copy-Item $nssmExe.FullName -Destination $NssmPath -Force
    Remove-Item -Recurse -Force $TempExtractDir
    Remove-Item -Force $TempZip
}


# 3. GitHub API for Releases (JSON)
$releaseApi = "https://api.github.com/repos/bjoernboeckle/mqtt-presence/releases/latest"
Write-Host "Looking up latest release using GitHub API..."
$release = Invoke-RestMethod -Uri $releaseApi -UseBasicParsing

# 4. Find exe using version in its name
$exeAsset = $release.assets | Where-Object { $_.name -match "^mqtt-presence-v[\d\.]+\.exe$" } | Select-Object -First 1
if (-not $exeAsset) {
    Write-Error "No executable found in release."
    exit 1
}

$exeName = $exeAsset.name
$exeUrl = $exeAsset.browser_download_url
$exePath = Join-Path $installDir $exeName

Write-Host "Downloading $exeName from:"
Write-Host "   $exeUrl"



# 5. Download EXE
Invoke-WebRequest -Uri $exeUrl -OutFile $exePath -UseBasicParsing


# 6. Remove service if required
if ((& $NssmPath status $serviceName) -match "SERVICE_NAME") {
    Write-Host "Removing existing service..."
    & $NssmPath stop $serviceName | Out-Null
    Start-Sleep -Seconds 3
    & $NssmPath remove $serviceName confirm | Out-Null
}

# 7. Install service
Write-Host "Installing service '$serviceName' with $exeName..."
& $NssmPath install $serviceName $exePath

# Working directories and Logs
& $NssmPath set $serviceName AppDirectory $installDir
& $NssmPath set $ServiceName AppParameters "$configArg $logArg"
& $NssmPath set $serviceName AppStdout (Join-Path $installDir "stdout.log")
& $NssmPath set $serviceName AppStderr (Join-Path $installDir "stderr.log")
& $NssmPath set $serviceName AppRotateFiles 1

# 8. Starting service
Write-Host "Starting service '$serviceName'..."
& $NssmPath start $serviceName

Write-Host "Installation complete. Service is running as '$exeName'."
