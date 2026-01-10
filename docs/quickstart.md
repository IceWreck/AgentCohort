# AgentCohort Quickstart

AgentCohort is a CLI tool for tracking and orchestrating tasks with dependencies.

## Basic Workflow

```bash
uvx git+https://github.com/IceWreck/AgentCohort.git task --help

# Create a task
uvx git+https://github.com/IceWreck/AgentCohort.git task create "Fix login bug" -p 0

# Start working on it
uvx git+https://github.com/IceWreck/AgentCohort.git task start <task_id>

# Close when done
uvx git+https://github.com/IceWreck/AgentCohort.git task close <task_id>
```

## Essential Commands

**Create tasks**
```bash
agentcohort task create "Title" [-p priority] [-t type]
# Types: bug, feature, task, epic, chore
# Priority: 0-4 (0=highest)
```

After creating a task, you can edit the markdown files:
- description.md - Task description
- design.md - Design details
- acceptance.md - Acceptance criteria

**List & filter**
```bash
agentcohort task ls                    # All tasks
agentcohort task ls --status open     # Filter by status
agentcohort task ready                # Ready to start (no blockers)
agentcohort task blocked              # Blocked by dependencies
agentcohort task closed               # Recently closed
```

**View details**
```bash
agentcohort task show <task_id>       # Full details
```

**Task lifecycle**
```bash
agentcohort task start <task_id>      # Mark in_progress
agentcohort task close <task_id>      # Mark closed
agentcohort task reopen <task_id>     # Reopen closed task
agentcohort task status <task_id> <new_status>
```

**Notes**
```bash
agentcohort task add-note <task_id>  # Creates a new note file
```

## Dependencies

```bash
# Task B depends on Task A (B blocked until A closes)
agentcohort task dep-add <task_id> <dep_id>

# Remove dependency
agentcohort task dep-remove <task_id> <dep_id>

# View dependency tree
agentcohort task dep-tree <task_id>
```

## Links

```bash
# Create bidirectional links between tasks
agentcohort task link <task_id1> <task_id2>

# Remove link
agentcohort task unlink <task_id> <target_id>
```

## Query (JSON export)

```bash
# Export all tasks as JSON
agentcohort task query

# Filter with jq (requires jq installed)
agentcohort task query '.[] | select(.status == "open")'
agentcohort task query '.[] | .id'
```

## Task IDs

All commands use short task IDs (e.g., `a-864a`). Create a task to get its ID, or use `agentcohort task ls` to see all IDs.
