<#
.SYNOPSIS
  Project dashboard auto-refresh: install / query / remove / run-once Windows scheduled task.

.DESCRIPTION
  Registers a task that rebuilds the offline dashboard every N minutes (default 15).
  All non-ASCII paths live in dashboard-task-config.json (UTF-8, no BOM), so this
  script stays ASCII-only and works under Windows PowerShell 5.1 (which scheduled
  tasks invoke) as well as PowerShell 7.

  The task calls this same script with -RunOnce, which reads the config and runs
  build_dashboard.py --once. No server, no service, no extra process to keep alive.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install_dashboard_task.ps1 `
    -Root "E:\Dev-2\<project parent>" -Out "<parent>\<workspace>\dashboard\index.html"

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install_dashboard_task.ps1 -Status
  powershell -ExecutionPolicy Bypass -File install_dashboard_task.ps1 -Uninstall
  powershell -ExecutionPolicy Bypass -File install_dashboard_task.ps1 -RunOnce
#>
[CmdletBinding()]
param(
    [string]$Root = "",
    [string]$Out = "",
    [int]$IntervalMinutes = 15,
    [switch]$RunOnce,
    [switch]$Status,
    [switch]$Uninstall
)
$ErrorActionPreference = "Stop"
$TaskName = "RebuildDashboard-AutoRefresh"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Generator = Join-Path $ScriptDir "build_dashboard.py"
$ConfigPath = Join-Path $ScriptDir "dashboard-task-config.json"

function Read-Config {
    if (Test-Path $ConfigPath) {
        return (Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json)
    }
    return $null
}
function Find-Python {
    $c = Get-Command python -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $c = Get-Command py -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    throw "python not found in PATH (need Python 3.10+)"
}
function Invoke-Once {
    $cfg = Read-Config
    if (-not $cfg) { throw "config missing: $ConfigPath (run install first)" }
    if (-not (Test-Path $Generator)) { throw "generator missing: $Generator" }
    $py = if ($cfg.python -and (Test-Path $cfg.python)) { $cfg.python } else { Find-Python }
    & $py $Generator --once --root $cfg.root --out $cfg.out --refresh-sec $cfg.refresh_sec
    if ($LASTEXITCODE -ne 0) { throw "generator failed, exit $LASTEXITCODE" }
}

if ($Status) {
    $q = & schtasks /Query /TN $TaskName /FO LIST /V 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Output "NOT_INSTALLED"; exit 1 }
    $q | Select-String -Pattern "TaskName|Status|Next Run|Schedule Type|Repeat|Minutes|任务名|状态|下次" |
        ForEach-Object { $_.Line }
    $cfg = Read-Config
    if ($cfg) {
        Write-Output ("CONFIG root={0} | out={1} | refresh_sec={2} | interval_minutes={3}" -f
            $cfg.root, $cfg.out, $cfg.refresh_sec, $cfg.interval_minutes)
    }
    exit 0
}
if ($Uninstall) {
    & schtasks /Delete /TN $TaskName /F 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Output "NOT_INSTALLED (nothing to remove)"; exit 0 }
    Write-Output "UNINSTALLED $TaskName"
    exit 0
}
if ($RunOnce) { Invoke-Once; exit 0 }

# ---------------- install ----------------
if (-not (Test-Path $Generator)) { throw "generator not found: $Generator" }
if (-not $Root) {
    $cfg = Read-Config
    if ($cfg) { $Root = $cfg.root; $Out = $cfg.out; $IntervalMinutes = $cfg.interval_minutes }
    else { throw "-Root is required when no config exists" }
}
if (-not $Out) { throw "-Out is required (full path to dashboard/index.html)" }
if ($IntervalMinutes -lt 1) { throw "-IntervalMinutes must be >= 1" }

$cfgObj = [ordered]@{
    root             = $Root
    out              = $Out
    refresh_sec      = $IntervalMinutes * 60
    interval_minutes = $IntervalMinutes
    python           = (Find-Python)
    generator        = $Generator
    task_name        = $TaskName
    created_at       = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}
$json = $cfgObj | ConvertTo-Json -Depth 3
[System.IO.File]::WriteAllText($ConfigPath, $json, (New-Object System.Text.UTF8Encoding($false)))

# $PSCommandPath has no spaces (skill package lives in a plain ASCII path),
# so /TR needs no nested quoting - avoids the classic schtasks quoting trap.
$tr = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $PSCommandPath -RunOnce"
& schtasks /Create /TN $TaskName /TR $tr /SC MINUTE /MO $IntervalMinutes /F /RL LIMITED 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "schtasks create failed (exit $LASTEXITCODE). Try running as administrator, or use build_dashboard.py --watch instead."
}

# Run once immediately so the dashboard is fresh right after install.
Invoke-Once
Write-Output "INSTALLED $TaskName | every $IntervalMinutes min | $Out"
Write-Output "TIP: -Status to inspect, -Uninstall to remove, -RunOnce to trigger manually."
