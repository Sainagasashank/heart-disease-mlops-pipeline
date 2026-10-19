<# Install a user-scoped `make` PowerShell function for this project. #>
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$ProfileDirectory = Split-Path -Parent $PROFILE.CurrentUserAllHosts
New-Item -ItemType Directory -Force -Path $ProfileDirectory | Out-Null
if (-not (Test-Path $PROFILE.CurrentUserAllHosts)) {
    New-Item -ItemType File -Force -Path $PROFILE.CurrentUserAllHosts | Out-Null
}
$MarkerStart = "# heart-assignment-make-start"
$MarkerEnd = "# heart-assignment-make-end"
$existing = Get-Content -Raw $PROFILE.CurrentUserAllHosts
$existing = if ($null -eq $existing) { "" } else { $existing }
$block = @"
$MarkerStart
function global:make {
    param([Parameter(ValueFromRemainingArguments = `$true)][string[]]`$Arguments)
    `$runner = Join-Path (Get-Location) 'Make.ps1'
    if (-not (Test-Path `$runner)) { throw 'No Make.ps1 in the current directory. Use GNU Make for non-project folders.' }
    & `$runner @Arguments
}
$MarkerEnd
"@
$pattern = "(?s)$([regex]::Escape($MarkerStart)).*?$([regex]::Escape($MarkerEnd))"
if ($existing -match $pattern) {
    $existing = [regex]::Replace($existing, $pattern, $block)
} else {
    $existing = $existing.TrimEnd() + [Environment]::NewLine + $block
}
Set-Content -Path $PROFILE.CurrentUserAllHosts -Value $existing -Encoding utf8
. $PROFILE.CurrentUserAllHosts
Write-Host "Installed the project make function. Open a new PowerShell or run: . `$PROFILE.CurrentUserAllHosts"
