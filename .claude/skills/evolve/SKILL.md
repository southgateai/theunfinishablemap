# Evolve

The main orchestrator for autonomous site evolution. Intelligently selects and executes tasks based on priority, staleness, and site goals.

## Usage

```
/evolve [mode]
```

Modes:
- `quick` - Execute 1 task (highest scored)
- (default) - Standard session, execute 2-3 tasks
- `deep` - Execute 3-5 tasks including maintenance

## Session Workflow

### 1. Load State

Read `obsidian/workflow/evolution-state.yaml` to get:
- Last run timestamps for maintenance tasks
- Failed task retry counts
- Content statistics

### 2. Check Staleness

For each maintenance task, check if overdue:

| Task | Cadence | Inject when overdue by |
|------|---------|------------------------|
| validate-all | 1 day | 2 days |
| pessimistic-review | 7 days | 3 days |
| optimistic-review | 7 days | 3 days |
| check-tenets | 30 days | 5 days |
| check-links | 7 days | 3 days |

Create synthetic tasks for overdue maintenance.

### 3. Load and Score Tasks

Read `obsidian/workflow/todo.md` and score all tasks:

```
SCORE = PRIORITY_BASE + STALENESS_BONUS + URGENCY_MOD - FAILURE_PENALTY

PRIORITY_BASE: P0=400, P1=300, P2=200, P3=100
STALENESS_BONUS: days_overdue * 20 (max 150) - for synthetic maintenance tasks
URGENCY_MOD: +50 critical issue, +30 medium issue, +20 has research
FAILURE_PENALTY: -100 per failure, -500 at 3+ failures
```

### 4. Select Tasks

Based on mode:
- **Quick**: Top 1 task
- **Standard**: Top 2-3 tasks (at least 1 content + 1 maintenance if overdue)
- **Deep**: Top 3-5 tasks

Never select:
- Tasks with 3+ failures (these are blocked)
- P3 tasks (require human promotion)
- Tasks with unmet dependencies

### 5. Execute Tasks

For each selected task:

1. If synthetic (maintenance): invoke the skill directly
   - `/validate-all`
   - `/pessimistic-review`
   - `/optimistic-review`
   - `/check-tenets`
   - `/check-links`

2. If queue task: invoke based on type
   - `expand-topic` → `/expand-topic [topic]`
   - `research-topic` → `/research-topic [topic]`
   - `refine-draft` → `/refine-draft [file]`

3. After each task:
   - Record outcome (success/failed/partial)
   - If failed: increment retry count in state
   - If 3+ failures: move to Blocked section in todo.md
   - If success: mark completed in todo.md

### 6. Update State

Update `obsidian/workflow/evolution-state.yaml`:
- `last_updated` timestamp
- `session_count` increment
- `last_runs` for any maintenance tasks executed
- `failed_tasks` counts
- `recent_tasks` history
- `content_stats` (recount files)
- `progress` metrics

### 7. Calculate Convergence

Compute convergence score (0-100%):
- 50% weight: Content breadth (topics, concepts, arguments written)
- 30% weight: Quality (critical/medium issues from reviews)
- 20% weight: Completeness (no placeholders)

### 8. Generate Report

Output session summary:

```markdown
## Evolution Session Complete

**Mode**: standard
**Tasks executed**: 3
**Duration**: ~15 minutes

### Tasks
1. ✓ Run pessimistic-review (overdue by 5 days) - Score: 350
2. ✓ Write article on hard problem - Score: 300
3. ✗ Research quantum decoherence - Failed (attempt 2/3)

### Metrics
- Convergence: 28% → 32%
- Content: 11 files (+1)
- Quality: 0 critical, 2 medium issues

### Next Session
Recommended tasks:
1. P1: Address circularity concern (Score: 300)
2. validate-all (due tomorrow)
```

### 9. Commit Changes

If any files were modified, create a single commit:

```
chore(auto): Evolution session - [summary]

Tasks: [list]
Convergence: [old]% → [new]%
```

Use AI authorship for the commit.

## Handling Failures

When a task fails:
1. Increment retry count in `failed_tasks`
2. Log the failure reason
3. If retry count reaches 3:
   - Move task to "## Blocked Tasks (Needs Human)" section in todo.md
   - Add explanation of failure pattern
   - Do not retry until human intervenes

## Blocked Tasks Section

When a task is blocked, add to todo.md:

```markdown
## Blocked Tasks (Needs Human)

### P1: [Task title]
- **Failures**: 3
- **Last attempt**: 2026-01-06
- **Error pattern**: [description of what went wrong]
- **Suggested action**: [how human might fix]
```

## State File Location

`obsidian/workflow/evolution-state.yaml`

## Dependencies

This skill uses:
- `tools/evolution/state.py` - State loading/saving
- `tools/evolution/scoring.py` - Task scoring
- `tools/evolution/staleness.py` - Staleness detection
- `tools/todo/processor.py` - Todo parsing

## Notes

- P3 tasks are never auto-selected; human must promote to P2+
- Synthetic maintenance tasks compete fairly via scoring
- Each session is atomic - either all changes commit or none
- The skill is designed for manual triggering (2-3x per week)
