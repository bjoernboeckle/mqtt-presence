$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

$url = 'https://github.com/bjoernboeckle/mqtt-presence/releases/download/v0.2.8/mqtt-presence-v0.2.8-setup.exe'
$checksum = '3052bb856eb9bcbcf0a7e7a2450bc1c8a57f986782080abe1139c092b8d1803a'
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
