#!/bin/bash
# Real Estate CRM - Persistent Start Script
# Keeps the CRM running in background with automatic restart

CRM_DIR="/home/ender/.claude/projects/offer-creator"
LOG_FILE="$CRM_DIR/crm_persistent.log"
PID_FILE="$CRM_DIR/crm.pid"

cd "$CRM_DIR"

# Kill existing process if running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Stopping existing CRM process (PID: $OLD_PID)"
        kill "$OLD_PID"
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# Export environment variables
export GEMINI_API_KEY="AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU"

# Start in background with nohup
echo "Starting Real Estate CRM on port 5001..."
echo "Access via: http://172.22.206.209:5001"
echo "Logs: $LOG_FILE"

source venv/bin/activate
nohup python core_app/real_estate_crm.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# Save PID for later management
echo "$NEW_PID" > "$PID_FILE"

echo "✅ CRM started successfully!"
echo "🌐 Windows Access: http://172.22.206.209:5001"
echo "📁 PID: $NEW_PID (saved to $PID_FILE)"
echo "📋 View logs: tail -f $LOG_FILE"
echo "🛑 Stop with: ./stop_crm.sh"