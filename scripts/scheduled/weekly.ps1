# Weekly automation script for SouthgateAI
# Runs: work-todo, refine-draft, pessimistic-review, optimistic-review
# Schedule: Various days via Windows Task Scheduler

param(
    [switch]$DryRun,
    [ValidateSet("work-todo", "refine-draft", "pessimistic-review", "optimistic-review", "crosslink")]
    [string]$Task = "work-todo",
    [int]$MaxTurns = 20
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "c:\Users\andy\Documents\sai\southgateai-main"
$ClaudePath = "C:\Users\andy\.local\bin\claude.exe"
$LogFile = "$ProjectRoot\obsidian\project\automation-log.txt"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Set-Location $ProjectRoot

function Write-Log {
    param([string]$Message)
    $LogEntry = "$Timestamp - $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Get-Cost {
    param($JsonResult)
    if ($JsonResult.cost_usd) {
        return $JsonResult.cost_usd
    }
    return "unknown"
}

Write-Log "Starting weekly automation: $Task"

if ($DryRun) {
    Write-Log "DRY RUN - No changes will be made"
    Write-Host "Would run: $ClaudePath -p `"/$Task`" --output-format json --max-turns $MaxTurns"
    exit 0
}

try {
    # Determine allowed tools based on task
    $allowedTools = "Bash,Read,Glob,Grep,Edit,Write"
    if ($Task -eq "work-todo" -or $Task -eq "research-topic") {
        $allowedTools += ",WebSearch"
    }

    # Build prompt based on task - skills don't work in non-interactive mode
    # so we include the full instructions
    $dateStr = Get-Date -Format 'yyyy-MM-dd'
    $prompt = switch ($Task) {
        "work-todo" {
@"
Execute the work-todo skill. Read .claude/skills/work-todo/SKILL.md for full instructions.

Summary:
1. Read obsidian/project/todo.md
2. Select the highest priority pending task (P0 > P1 > P2 > P3)
3. Execute it based on type (expand-topic, research-topic, refine-draft, etc.)
4. Update todo.md to mark task complete
5. Log to obsidian/project/changelog.md
6. Do NOT commit - the script handles commits
"@
        }
        "refine-draft" {
@"
Execute the refine-draft skill. Read .claude/skills/refine-draft/SKILL.md for full instructions.

Summary:
1. Find the oldest draft content in obsidian/
2. Review and improve the content
3. Update ai_modified timestamp in frontmatter
4. Keep draft: true (human must approve)
5. Log to obsidian/project/changelog.md
"@
        }
        "pessimistic-review" {
@"
Execute the pessimistic-review skill. Read .claude/skills/pessimistic-review/SKILL.md for full instructions.

Summary:
1. Review all non-draft content in obsidian/topics/, concepts/, tenets/
2. Analyze from critic perspectives (Churchland, Dennett, Tegmark, Deutsch, Popper, Nagarjuna)
3. Find logical gaps, unsupported claims, contradictions
4. Create report at obsidian/project/reviews/pessimistic-$dateStr.md
5. Add actionable items to todo.md
6. Log to changelog.md
"@
        }
        "optimistic-review" {
@"
Execute the optimistic-review skill. Read .claude/skills/optimistic-review/SKILL.md for full instructions.

Summary:
1. Review all non-draft content in obsidian/topics/, concepts/, tenets/
2. Analyze from sympathetic perspectives (Chalmers, Stapp, Nagel, Whitehead, Kane, McGinn)
3. Identify strengths and expansion opportunities
4. Create report at obsidian/project/reviews/optimistic-$dateStr.md
5. Add suggested topics to todo.md
6. Log to changelog.md
"@
        }
        "crosslink" {
            "Run: uv run python scripts/curate.py crosslink hugo/content/ --apply"
        }
        default {
            "Execute the $Task task"
        }
    }

    # Run the task
    $startTime = Get-Date
    $result = & $ClaudePath -p $prompt --output-format json --max-turns $MaxTurns --allowedTools $allowedTools 2>&1
    $endTime = Get-Date
    $duration = $endTime - $startTime

    # Try to parse JSON result
    try {
        $jsonResult = $result | ConvertFrom-Json
        $cost = Get-Cost $jsonResult
        Write-Log "Task completed - Duration: $($duration.TotalMinutes)m, Cost: $cost"
    }
    catch {
        Write-Log "Task completed - Duration: $($duration.TotalMinutes)m (could not parse cost)"
    }

    # Stage any changes
    git add -A

    # Check if there are changes to commit
    git diff --staged --quiet
    $hasChanges = $LASTEXITCODE -ne 0

    if ($hasChanges) {
        $dayOfWeek = (Get-Date).DayOfWeek
        $commitMsg = "chore(auto): Weekly $Task ($dayOfWeek) - $(Get-Date -Format 'yyyy-MM-dd')"
        git commit -m $commitMsg --author="southgate.ai Agent <agent@southgate.ai>"
        Write-Log "Changes committed: $commitMsg"
    }
    else {
        Write-Log "No changes to commit"
    }
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}

Write-Log "Weekly automation complete"
