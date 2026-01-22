# AgentCohort CLI Documentation

This document contains the help text for all CLI commands.

## Main Command

```
                                                                                
 Usage: agentcohort [OPTIONS] COMMAND [ARGS]...                                 
                                                                                
 AgentCohort - Agent Task Tracking & Orchestration Tool.                        
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ task       Task tracking and management.                                     │
│ worktree   Git worktree management.                                          │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task`

```
                                                                                
 Usage: agentcohort task [OPTIONS] COMMAND [ARGS]...                            
                                                                                
 Task tracking and management.                                                  
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ create       Create a new task with the specified properties.                │
│ start        Mark a task as in_progress.                                     │
│ close        Mark a task as closed.                                          │
│ reopen       Reopen a closed task (sets status back to open).                │
│ status       Set the status of a task to the specified value.                │
│ ls           List all tasks, optionally filtering by status.                 │
│ ready        List tasks that are ready to be started (no blocking            │
│              dependencies).                                                  │
│ blocked      List tasks that are blocked by unclosed dependencies.           │
│ closed       List recently closed tasks.                                     │
│ show         Display detailed information about a task including related     │
│              tasks.                                                          │
│ add-note     Add a note to a task.                                           │
│ query        Query tasks and export as JSON.                                 │
│ dep-add      Add a dependency from task_id to dep_id.                        │
│ dep-remove   Remove a dependency from task_id to dep_id.                     │
│ dep-tree     Display the dependency tree for a task.                         │
│ undep        Remove a dependency from task_id to dep_id (alias for           │
│              dep-remove).                                                    │
│ link         Create bidirectional links between multiple tasks.              │
│ unlink       Remove a link between two tasks.                                │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task create`

```
                                                                                
 Usage: agentcohort task create [OPTIONS] TITLE                                 
                                                                                
 Create a new task with the specified properties.                               
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    title      TEXT  [required]                                             │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --type          -t      [bug|feature|task|epic|ch  Task type.                │
│                         ore]                       [default: task]           │
│ --priority      -p      INTEGER                    Task priority (0-4,       │
│                                                    0=highest).               │
│                                                    [default: 2]              │
│ --assignee      -a      TEXT                       Task assignee.            │
│ --external-ref          TEXT                       External reference.       │
│ --parent                TEXT                       Parent task id.           │
│ --help                                             Show this message and     │
│                                                    exit.                     │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task start`

```
                                                                                
 Usage: agentcohort task start [OPTIONS] TASK_ID                                
                                                                                
 Mark a task as in_progress.                                                    
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task close`

```
                                                                                
 Usage: agentcohort task close [OPTIONS] TASK_ID                                
                                                                                
 Mark a task as closed.                                                         
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task reopen`

```
                                                                                
 Usage: agentcohort task reopen [OPTIONS] TASK_ID                               
                                                                                
 Reopen a closed task (sets status back to open).                               
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task status`

```
                                                                                
 Usage: agentcohort task status [OPTIONS] TASK_ID                               
                                NEW_STATUS:{open|in_progress|closed}            
                                                                                
 Set the status of a task to the specified value.                               
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id         TEXT                        [required]                  │
│ *    new_status      NEW_STATUS:{open|in_progre  [required]                  │
│                      ss|closed}                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task ls`

```
                                                                                
 Usage: agentcohort task ls [OPTIONS]                                           
                                                                                
 List all tasks, optionally filtering by status.                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --status        [open|in_progress|closed]  Filter by status.                 │
│ --help                                     Show this message and exit.       │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task ready`

```
                                                                                
 Usage: agentcohort task ready [OPTIONS]                                        
                                                                                
 List tasks that are ready to be started (no blocking dependencies).            
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task blocked`

```
                                                                                
 Usage: agentcohort task blocked [OPTIONS]                                      
                                                                                
 List tasks that are blocked by unclosed dependencies.                          
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task closed`

```
                                                                                
 Usage: agentcohort task closed [OPTIONS]                                       
                                                                                
 List recently closed tasks.                                                    
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --limit        INTEGER  Number of tasks to show. [default: 20]               │
│ --help                  Show this message and exit.                          │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task show`

```
                                                                                
 Usage: agentcohort task show [OPTIONS] TASK_ID                                 
                                                                                
 Display detailed information about a task including related tasks.             
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task add-note`

```
                                                                                
 Usage: agentcohort task add-note [OPTIONS] TASK_ID                             
                                                                                
 Add a note to a task.                                                          
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task query`

```
                                                                                
 Usage: agentcohort task query [OPTIONS] [JQ_FILTER]                            
                                                                                
 Query tasks and export as JSON.                                                
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   jq_filter      [JQ_FILTER]                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task dep-add`

```
                                                                                
 Usage: agentcohort task dep-add [OPTIONS] TASK_ID DEP_ID                       
                                                                                
 Add a dependency from task_id to dep_id.                                       
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
│ *    dep_id       TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task dep-remove`

```
                                                                                
 Usage: agentcohort task dep-remove [OPTIONS] TASK_ID DEP_ID                    
                                                                                
 Remove a dependency from task_id to dep_id.                                    
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
│ *    dep_id       TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task dep-tree`

```
                                                                                
 Usage: agentcohort task dep-tree [OPTIONS] TASK_ID                             
                                                                                
 Display the dependency tree for a task.                                        
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --full          Show all occurrences.                                        │
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task undep`

```
                                                                                
 Usage: agentcohort task undep [OPTIONS] TASK_ID DEP_ID                         
                                                                                
 Remove a dependency from task_id to dep_id (alias for dep-remove).             
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id      TEXT  [required]                                           │
│ *    dep_id       TEXT  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task link`

```
                                                                                
 Usage: agentcohort task link [OPTIONS] TASK_IDS...                             
                                                                                
 Create bidirectional links between multiple tasks.                             
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_ids      TASK_IDS...  [required]                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort task unlink`

```
                                                                                
 Usage: agentcohort task unlink [OPTIONS] TASK_ID TARGET_ID                     
                                                                                
 Remove a link between two tasks.                                               
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    task_id        TEXT  [required]                                         │
│ *    target_id      TEXT  [required]                                         │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort worktree`

```
                                                                                
 Usage: agentcohort worktree [OPTIONS] COMMAND [ARGS]...                        
                                                                                
 Git worktree management.                                                       
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ create   Create a new worktree.                                              │
│ ls       List all worktrees.                                                 │
│ remove   Remove a worktree.                                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort worktree create`

```
                                                                                
 Usage: agentcohort worktree create [OPTIONS] NAME                              
                                                                                
 Create a new worktree.                                                         
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    name      TEXT  [required]                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --branch      -b      TEXT  Branch name (defaults to <name>).                │
│ --base                TEXT  Base branch to create from (defaults to current  │
│                             branch).                                         │
│ --existing                  Use existing branch instead of creating new one. │
│ --path                TEXT  Custom worktree path (defaults to                │
│                             ../<repo-name>-<name>).                          │
│ --post-setup          TEXT  Command to run after creation (e.g., "uv sync"). │
│ --help                      Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort worktree ls`

```
                                                                                
 Usage: agentcohort worktree ls [OPTIONS]                                       
                                                                                
 List all worktrees.                                                            
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## `agentcohort worktree remove`

```
                                                                                
 Usage: agentcohort worktree remove [OPTIONS] NAME                              
                                                                                
 Remove a worktree.                                                             
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    name      TEXT  [required]                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --force          Force removal even if worktree has changes.                 │
│ --help           Show this message and exit.                                 │
╰──────────────────────────────────────────────────────────────────────────────╯


```
