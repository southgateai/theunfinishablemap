---
title: Workflow System
created: 2026-01-05
modified: 2026-01-05
human_modified: 2026-01-05
ai_modified:
draft: false
topics: []
concepts: []
related_articles:
  - "[[automation]]"
  - "[[todo]]"
  - "[[changelog]]"
ai_contribution: 100
author: Andy Southgate
ai_system: claude-opus-4-5-20251101
ai_generated_date: 2026-01-05
last_curated:
---

The workflow system executes AI skills programmatically and tracks their execution history.

## Overview

Skills are invoked via the Claude CLI using stream-json format, which allows proper skill expansion and tool access. The workflow executor:

1. Invokes a skill by name
2. Captures execution metrics (duration, cost, turns)
3. Logs results to this file
4. Optionally commits changes with AI authorship

## Available Skills

| Skill | Purpose | Modifies Content? |
|-------|---------|-------------------|
| `/validate-all` | Check frontmatter, links, orphans | No (reports only) |
| `/check-tenets` | Verify alignment with 5 tenets | No (reports only) |
| `/pessimistic-review` | Find logical gaps and weaknesses | No (reports only) |
| `/optimistic-review` | Find strengths and opportunities | No (reports only) |
| `/research-topic` | Web research, outputs notes | Research notes only |
| `/expand-topic` | Generate new article | Yes (creates content) |
| `/refine-draft` | Improve existing content | Yes (edits content) |
| `/work-todo` | Execute highest priority task | Depends on task |
| `/check-links` | Verify all internal links work | No (reports only) |

## Running Workflows

### From Command Line

```bash
# Run a skill
uv run python scripts/run_workflow.py validate-all

# Dry run (see what would happen)
uv run python scripts/run_workflow.py work-todo --dry-run

# Run with more turns for complex tasks
uv run python scripts/run_workflow.py expand-topic --max-turns 30

# Run and commit changes
uv run python scripts/run_workflow.py work-todo --commit
```

### From PowerShell Scripts

The scheduled scripts in `scripts/scheduled/` call the workflow executor:

```powershell
# Daily validation
.\scripts\scheduled\daily.ps1

# Weekly tasks
.\scripts\scheduled\weekly.ps1 -Task work-todo
```

## Execution Format

Each workflow execution logs:

- **Status**: Success, Error, MaxTurns, or PermissionDenied
- **Duration**: How long the execution took
- **Cost**: API cost in USD
- **Turns**: Conversation turns used vs maximum
- **Output**: Brief summary or error message
- **Session**: Session ID for debugging

## Recent Executions

