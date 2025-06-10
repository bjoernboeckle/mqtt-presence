$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

$url = 'https://github.com/bjoernboeckle/mqtt-presence/releases/download/v0.2.6/mqtt-presence-v0.2.6-setup.exe'
$checksum = 'defa7cf1cfee7e66392b995f985489fbd1ef9f6da6d5ce074984170fd4cf1543'
$checksumType = 'sha256'


$packageArgs = @{
  packageName   = $env:ChocolateyPackageName
  unzipLocation = $toolsDir
  fileType      = 'EXE'
  url           = $url
  softwareName  = 'mqtt-presence*'
  checksum      = $checksum
  checksumType  = $checksumType
  silentArgs   = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  validExitCodes= @(0, 3010, 1641)
}

Install-ChocolateyPackage @packageArgs
