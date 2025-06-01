#!/bin/bash
# Stop the Real Estate CRM persistent process

CRM_DIR="/home/ender/.claude/projects/offer-creator"
PID_FILE="$CRM_DIR/crm.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping Real Estate CRM (PID: $PID)"
        kill "$PID"
        sleep 2
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Force killing CRM process"
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        echo "✅ CRM stopped successfully"
    else
        echo "⚠️ CRM process not running (stale PID file)"
        rm -f "$PID_FILE"
    fi
else
    echo "⚠️ No PID file found - CRM may not be running"
fi