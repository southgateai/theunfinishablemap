# Monthly automation script for The Unfinishable Map
# Runs: check-tenets, progress-report
# Schedule: 1st and 15th of month via Windows Task Scheduler

param(
    [switch]$DryRun,
    [ValidateSet("check-tenets", "progress-report")]
    [string]$Task = "check-tenets",
    [int]$MaxTurns = 20
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "c:\Users\andy\Documents\sai\southgateai-main"
$UvPath = "C:\Users\andy\.local\bin\uv.exe"
$LogFile = "$ProjectRoot\obsidian\workflow\automation-log.txt"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Set-Location $ProjectRoot

function Write-Log {
    param([string]$Message)
    $LogEntry = "$Timestamp - $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

Write-Log "Starting monthly automation: $Task"

if ($DryRun) {
    Write-Log "DRY RUN - No changes will be made"
    & $UvPath run python scripts/run_workflow.py $Task --dry-run
    exit 0
}

try {
    # Run the workflow executor
    & $UvPath run python scripts/run_workflow.py $Task --commit --max-turns $MaxTurns
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Log "Task completed successfully"
    }
    elseif ($exitCode -eq 2) {
        Write-Log "Task hit max turns limit"
    }
    else {
        Write-Log "Task failed with exit code $exitCode"
        exit $exitCode
    }
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}

Write-Log "Monthly automation complete"
