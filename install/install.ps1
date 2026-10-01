# Install apk-rebuild-skills: create directory junctions from skills/* into agent skill dirs.
# Usage: powershell -ExecutionPolicy Bypass -File install/install.ps1 [-Targets workbuddy,claude,codex] [-Copy]
param(
    [string[]]$Targets = @("workbuddy"),
    [switch]$Copy
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$src = Join-Path $repo "skills"
$map = @{
    "workbuddy" = Join-Path $HOME ".workbuddy\skills"
    "claude"    = Join-Path $HOME ".claude\skills"
    "codex"     = Join-Path $HOME ".codex\skills"
}
foreach ($t in $Targets) {
    if (-not $map.ContainsKey($t)) { Write-Warning "unknown target: $t"; continue }
    $dst = $map[$t]
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
        if ($Copy) { Copy-Item -Recurse $_.FullName $link }
        else { New-Item -ItemType Junction -Path $link -Target $_.FullName | Out-Null }
        Write-Host "[$t] $($_.Name) -> $link"
    }
}
Write-Host "Done. Restart your agent tool to load the skills. Update later with: git pull"
