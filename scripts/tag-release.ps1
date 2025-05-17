param (
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$tag = "v$Version"

git tag $tag
git push origin $tag

Write-Host "✅ Release-Tag '$tag' wurde erfolgreich erstellt und gepusht."
