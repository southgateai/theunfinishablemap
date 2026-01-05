---
name: work-todo
description: Pick and execute the highest priority task from the todo queue. Content is published directly.
---

# Work Todo

Orchestrator skill that picks the highest priority task from the queue and executes it.

## When to Use

- Scheduled automated runs (Mon/Thu)
- When `/work-todo` is invoked
- When looking for the next task to work on

## Instructions

### 1. Process Todo Queue

Run the todo processor script to handle vetoed items and get the next task:

```bash
uv run python scripts/process_todo.py process --json
```

This script:
1. Finds any tasks tagged with `#veto` in the Active Tasks section
2. Moves them to the Vetoed Tasks section (removing the tag)
3. Returns the highest priority pending task

The output is JSON:
```json
{
  "modified": true,
  "vetoed": [{"title": "...", "priority": 2, ...}],
  "next_task": {"title": "...", "priority": 1, "type": "expand-topic", ...}
}
```

If `next_task` is `null`, there are no pending tasks.

### 2. Check for Work

If `next_task` is `null`:
- Log to changelog that no tasks were available
- Exit without error

### 3. Execute Based on Type

#### Type: `expand-topic`
Run the `/expand-topic` skill with the topic from the task.

#### Type: `research-topic`
Run the `/research-topic` skill with the topic from the task.

#### Type: `refine-draft`
Run the `/refine-draft` skill with the file from the task.

#### Type: `validate-all`
Run the `/validate-all` skill.

#### Type: `check-tenets`
Run the `/check-tenets` skill.

#### Type: `pessimistic-review`
Run the `/pessimistic-review` skill.

#### Type: `optimistic-review`
Run the `/optimistic-review` skill.

#### Type: Other
Execute the task directly based on its description.

### 4. Update Todo Queue

After task completion, update `obsidian/workflow/todo.md`:

Move the task from "Active Tasks" to "Completed Tasks":

```markdown
## Completed Tasks

### ✓ YYYY-MM-DD: [Task title]
- **Type**: [type]
- **Result**: [brief result]
- **Output**: [file created/modified, if any]
```

### 5. Handle Subtasks

If the task revealed additional work needed:

Add new tasks to the Active Tasks section with appropriate priority:
```markdown
### P2: [New subtask]
- **Type**: [type]
- **Status**: pending
- **Notes**: Discovered while working on [parent task]
```

### 6. Log to Changelog

Append to `obsidian/workflow/changelog.md`:
```markdown
### HH:MM - work-todo
- **Status**: Success/Partial/Failed
- **Task**: "[task title]"
- **Type**: [task type]
- **Duration**: Xm Ys
- **Output**: [what was produced]
- **Subtasks added**: [count or "None"]
```

### 7. Commit

Create a git commit with message describing what was done:
```
feat(content): [Description based on task type]

Task: [task title]
Type: [type]
[Additional context]
```

## Task Selection Rules

### Never Select
- Tasks with `Status: in-progress` (already being worked)
- Tasks with `Status: blocked`
- Tasks with unmet `Blocked-by` dependencies
- Tasks in the Vetoed Tasks section

Note: The `process_todo.py` script handles task selection automatically. It skips blocked/in-progress tasks and returns the highest priority pending task.

### Limit
- Only execute ONE task per invocation
- If task is very large, complete a reasonable chunk and note remaining work

## Error Handling

If a task fails:
1. Do NOT mark it complete
2. Update its status to note the failure
3. Add notes about what went wrong
4. Log the failure to changelog
5. Create a subtask if a specific fix is needed

```markdown
### P1: [Original task]
- **Type**: [type]
- **Status**: failed
- **Notes**: Failed on YYYY-MM-DD: [error description]
```

## Important

- Execute only ONE task per invocation
- Always update todo.md after completion
- Always log to changelog.md
- Create commits for all changes
- Don't skip tasks without reason
