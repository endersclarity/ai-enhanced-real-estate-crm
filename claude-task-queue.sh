#!/bin/bash
# Claude Code Task Queue Runner

TASK_DIR="/tmp/claude-tasks"
mkdir -p "$TASK_DIR"

# Function to add a task
add_task() {
    local task_id=$(date +%s)
    local task_desc="$1"
    echo "$task_desc" > "$TASK_DIR/pending_$task_id.task"
    echo "Task $task_id added: $task_desc"
}

# Function to run pending tasks
run_tasks() {
    for task_file in "$TASK_DIR"/pending_*.task; do
        [ -f "$task_file" ] || continue
        
        task_id=$(basename "$task_file" | sed 's/pending_\(.*\)\.task/\1/')
        task_desc=$(cat "$task_file")
        
        echo "Starting task $task_id: $task_desc"
        mv "$task_file" "$TASK_DIR/running_$task_id.task"
        
        # Run Claude Code in headless mode
        claude --no-interactive "$task_desc" > "$TASK_DIR/output_$task_id.log" 2>&1
        
        # Mark as complete
        mv "$TASK_DIR/running_$task_id.task" "$TASK_DIR/complete_$task_id.task"
        echo "Task $task_id completed"
    done
}

# Function to check task status
check_status() {
    echo "=== Task Status ==="
    echo "Pending: $(ls -1 "$TASK_DIR"/pending_*.task 2>/dev/null | wc -l)"
    echo "Running: $(ls -1 "$TASK_DIR"/running_*.task 2>/dev/null | wc -l)"
    echo "Complete: $(ls -1 "$TASK_DIR"/complete_*.task 2>/dev/null | wc -l)"
}

# Main command
case "$1" in
    add)
        add_task "$2"
        ;;
    run)
        run_tasks
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {add|run|status}"
        ;;
esac
