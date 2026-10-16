# Install apk-rebuild-skills into agent skill dirs.
# Usage:
#   powershell -ExecutionPolicy Bypass -File install/install.ps1 [-Targets workbuddy,claude,codex,trae] [-Copy] [-Dest <dir>]
# Notes:
#   - Default mode = directory junction (updates follow `git pull`). Junctions need a LOCAL source,
#     so when the repo lives on a network share (e.g. Y:\ mapped NAS / UNC path) the script
#     automatically switches to -Copy. Re-run the script after `git pull` to refresh copies.
#   - codex target honours $env:CODEX_HOME (falls back to ~/.codex).
#   - -Dest installs into an arbitrary skills dir (ignores -Targets).
param(
    [string[]]$Targets = @("workbuddy"),
    [switch]$Copy,
    [string]$Dest
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$src = Join-Path $repo "skills"

# Network source -> junction impossible -> force copy
$isNetwork = $repo.StartsWith("\\")
if (-not $isNetwork) {
    $drive = (Split-Path -Qualifier $repo).TrimEnd(':')
    $psd = Get-PSDrive -Name $drive -ErrorAction SilentlyContinue
    if ($psd -and $psd.DisplayRoot -and $psd.DisplayRoot.StartsWith("\\")) { $isNetwork = $true }
}
if ($isNetwork -and -not $Copy) {
    Write-Host "Source is on a network share ($repo); switching to -Copy mode."
    $Copy = $true
}

$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$map = @{
    "workbuddy" = Join-Path $HOME ".workbuddy\skills"
    "claude"    = Join-Path $HOME ".claude\skills"
    "codex"     = Join-Path $codexHome "skills"
    "trae"      = Join-Path $HOME ".trae-cn\skills"
}
$dests = @()
if ($Dest) { $dests += ,@("custom", $Dest) }
else {
    foreach ($t in $Targets) {
        if (-not $map.ContainsKey($t)) { Write-Warning "unknown target: $t"; continue }
        $dests += ,@($t, $map[$t])
    }
}

foreach ($pair in $dests) {
    $t = $pair[0]; $dst = $pair[1]
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Get-ChildItem -Directory $src | ForEach-Object {
        $link = Join-Path $dst $_.Name
        if (Test-Path $link) {
            $item = Get-Item $link -Force
            if ($item.LinkType) { $item.Delete() }
            else {
                $bak = "$link.bak-$(Get-Date -Format yyyyMMddHHmmss)"
                Move-Item $link $bak
                Write-Host "  existing dir backed up -> $bak"
            }
        }
        if ($Copy) {
            Copy-Item -Recurse $_.FullName $link
            foreach ($pc in @(Get-ChildItem -LiteralPath $link -Recurse -Directory -Filter "__pycache__")) {
                Microsoft.PowerShell.Management\Remove-Item -LiteralPath $pc.FullName -Recurse -Force
            }
        }
        else { New-Item -ItemType Junction -Path $link -Target $_.FullName | Out-Null }
        $ver = (Select-String -Path (Join-Path $link "SKILL.md") -Pattern "^version:\s*(.+)$" | Select-Object -First 1).Matches.Groups[1].Value
        Write-Host "[$t] $($_.Name) $ver -> $link"
    }
}
Write-Host "Done. Restart your agent tool (or open a new session) to load the skills."
if ($Copy) { Write-Host "Copy mode: after 'git pull' re-run this script to update." }
else { Write-Host "Junction mode: 'git pull' in $repo updates all agents." }
