$ErrorActionPreference = 'Stop'

$packageName = 'mqtt-presence'
$installerType = 'exe'
$url = 'https://github.com/BjoernBoeckle/mqtt-presence/releases/download/v__VERSION__/mqtt-presence-v__VERSION__-setup.exe'
$checksum = '__CHECKSUM__'
$checksumType = 'sha256'
$silentArgs = '/SILENT'

Install-ChocolateyPackage $packageName $installerType $silentArgs $url `
  -Checksum $checksum `
  -ChecksumType $checksumType
